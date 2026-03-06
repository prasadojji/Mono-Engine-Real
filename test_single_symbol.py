import logging
import pandas as pd
import sqlite3
import yaml
from datetime import datetime
from collections import defaultdict
from tabulate import tabulate
import json
import re
import sys
import os

# Add mono_engine to path
sys.path.append('.')

from mono_engine.modules.stoploss import StoplossModule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

quantity = config.get('stoploss_params', {}).get('quantity', 900)

# Test with just one symbol - recent Sensex option
TEST_SYMBOL = 'OPTIDX_SENSEX_BFO_2026-02-26_82000_CE'  # ATM call option
TEST_DB_SYMBOL = TEST_SYMBOL  # Same for options

# Connect to DB
conn = sqlite3.connect('mono_engine_data.db')

def load_data(db_symbol, days_back=7):
    """Load recent data for testing"""
    query = f"""
        SELECT timestamp as time, open, high, low, close, volume
        FROM historical_1min
        WHERE symbol = ?
        AND timestamp >= datetime('now', '-{days_back} days')
        ORDER BY timestamp
    """
    df = pd.read_sql_query(query, conn, params=(db_symbol,))
    if df.empty:
        return df
    df['time'] = pd.to_datetime(df['time'])
    return df.set_index('time')

# Mock event dispatcher
class MockEvents:
    def __init__(self):
        self.handlers = defaultdict(list)

    def subscribe(self, event, handler):
        self.handlers[event].append(handler)

    def unsubscribe(self, event, handler):
        if event in self.handlers:
            self.handlers[event].remove(handler)

    def publish(self, event, data):
        for handler in self.handlers.get(event, []):
            handler(data)

# Mock engine with event bus
class MockEngine:
    def __init__(self, config):
        self.config = config
        self.events = MockEvents()
        # Mock required attributes
        self.session = None  # Not needed for stoploss testing
        self.streamer = None  # Not needed for stoploss testing
        self.modules = {
            'state': MockState()
        }

    def subscribe(self, event, handler):
        self.events.subscribe(event, handler)

    def publish(self, event, data):
        self.events.publish(event, data)

class MockState:
    def __init__(self):
        self.trades = {}

    def is_in_trade(self, symbol=None):
        return True  # Always in trade for testing

    def get_entry_details(self, symbol=None):
        return MockEntryDetails()

class MockEntryDetails:
    def __init__(self):
        self.quantity = 900

# Test single symbol
logger.info(f"Testing stoploss with symbol: {TEST_SYMBOL}")

try:
    df_1min = load_data(TEST_DB_SYMBOL, days_back=7)
    if df_1min.empty:
        logger.error(f"No data found for {TEST_SYMBOL}")
        exit(1)

    logger.info(f"Loaded {len(df_1min)} 1-min bars for {TEST_SYMBOL}")
    logger.info(f"Date range: {df_1min.index[0]} to {df_1min.index[-1]}")

    mock_engine = MockEngine(config)
    stoploss = StoplossModule(mock_engine)
    stoploss.start()  # Start the stoploss module to subscribe to events

    # Subscribe to exit_signal and handle actual exit
    exit_triggered = False
    exit_price = None
    exit_time = None
    exit_reason = None

    def handle_exit(event):
        global exit_triggered, exit_price, exit_time, exit_reason
        exit_triggered = True
        exit_price = event['exit_price']
        exit_time = event['time']
        exit_reason = event['reason']
        logger.info(f"STOPLOSS EXIT: {event}")

    mock_engine.subscribe('exit_signal', handle_exit)

    # Start position at first close price (simulating entry)
    entry_price = df_1min['close'].iloc[0]
    entry_time = df_1min.index[0]

    mock_engine.publish('trade_entered', {
        'symbol': TEST_SYMBOL,
        'entry_price': entry_price
    })

    logger.info(f"Simulated entry at {entry_price:.2f}")

    # Feed bars to stoploss (simulate historical backtest)
    stop_loss_level = entry_price * 0.98  # 2% below entry
    print(f"2% Stop Loss Level: {stop_loss_level:.2f}")

    for i, (idx, row) in enumerate(df_1min.iterrows()):
        if exit_triggered:
            break  # Stop processing if exit was triggered

        current_close = float(row['close'])

        # Debug: Check if price went below stop
        if current_close < stop_loss_level:
            print(f"Bar {i}: Close {current_close:.2f} < Stop {stop_loss_level:.2f} - Should trigger exit!")

        bar_data = {
            'symbol': TEST_SYMBOL,
            'bar': {
                'ts': idx,
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': current_close,
                'volume': int(row['volume'])
            }
        }
        mock_engine.publish('1min_bar_closed', bar_data)

        # Check if stoploss triggered
        # In real implementation, this would be handled by event subscription
        # For testing, we'll check the monitor state

        if i % 100 == 0:  # Print every 100 bars
            monitor_state = stoploss.monitor[TEST_SYMBOL]
            print(f"Bar {i}: Close={current_close:.2f}, MaxProfit={monitor_state['max_profit']:.2f}%, TrailFlag={monitor_state['trail_start_flag']}")

    # Check final state
    monitor_state = stoploss.monitor[TEST_SYMBOL]

    if exit_triggered:
        final_pnl = (exit_price - entry_price) * quantity
        final_close = exit_price
    else:
        final_pnl = (df_1min['close'].iloc[-1] - entry_price) * quantity
        final_close = df_1min['close'].iloc[-1]

    print("\n" + "="*60)
    print(f"STOPLOSS TEST RESULTS for {TEST_SYMBOL}")
    print("="*60)
    print(f"Entry Price: {entry_price:.2f}")
    print(f"Entry Time: {entry_time}")
    print(f"Max Profit Reached: {monitor_state['max_profit']:.2f}%")
    print(f"Breakeven Flag: {monitor_state['breakeven_flag']}")
    print(f"Profit Lock Flag: {monitor_state['profit_lock_flag']}")
    print(f"Trail Start Flag: {monitor_state['trail_start_flag']}")
    print(f"Trail Stop Level: {monitor_state['trail_stop']:.2f}")
    print(f"Final PnL: {final_pnl:.2f}")
    print(f"Exit Triggered: {'YES' if exit_triggered else 'NO'}")
    if exit_triggered:
        print(f"Exit Price: {exit_price:.2f}")
        print(f"Exit Time: {exit_time}")
        print(f"Exit Reason: {exit_reason}")
    print("="*60)

except Exception as e:
    logger.error(f"Error testing {TEST_SYMBOL}: {e}")
    import traceback
    traceback.print_exc()

conn.close()