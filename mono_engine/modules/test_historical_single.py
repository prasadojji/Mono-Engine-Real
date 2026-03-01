# mono_engine/modules/test_historical_single.py
"""
Minimal Single Symbol Test - Truly Clean & Working Version
- Only tests SENSEX 05MAR 81200 PE
- No full engine, no market_data, no backfill
- Detailed debug of stoploss monitor every 100 bars
- Forces buy and final sell
"""

import logging
import sqlite3
import pandas as pd
from datetime import datetime

# Direct imports (minimal)
from mono_engine.modules.state import StateModule
from mono_engine.modules.stoploss import StoplossModule
from mono_engine.strategies.strategy import StrategyModule

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DummyEngine:
    """Dummy engine to satisfy BaseModule requirements"""
    def __init__(self):
        self.events = type('obj', (object,), {
            'publish': lambda self, name, data: None,
            'subscribe': lambda self, name, func: None,
            'unsubscribe': lambda self, name, func: None
        })()
        self.session = None
        self.modules = {}
        self.mode = "historical"

def test_single_symbol():
    logger.info("=" * 100)
    logger.info("🚀 MINIMAL SINGLE SYMBOL TEST v5")
    logger.info("Symbol: SENSEX 05MAR 81200 PE")
    logger.info("=" * 100)

    engine = DummyEngine()

    state_module = StateModule(engine)
    strategy_module = StrategyModule(engine)
    stoploss_module = StoplossModule(engine)

    engine.modules['state'] = state_module
    engine.modules['strategy'] = strategy_module
    engine.modules['stoploss'] = stoploss_module

    symbol = "SENSEX 05MAR 81200 PE"
    db_path = 'mono_engine_data.db'

    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f"""
        SELECT timestamp as ts, open, high, low, close, volume
        FROM historical_1min
        WHERE symbol = '{symbol}'
        ORDER BY timestamp
    """, conn, parse_dates=['ts'], index_col='ts')
    conn.close()

    if df.empty:
        logger.error("No data found for this symbol!")
        return

    logger.info(f"Loaded {len(df)} bars for {symbol}")

    df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low',
                          'close': 'Close', 'volume': 'Volume'})

    strategy = strategy_module._get_or_create_strategy(symbol)
    strategy.reset_day()

    recorded_sells = 0

    def on_exit(data):
        nonlocal recorded_sells
        recorded_sells += 1
        price = data.get('exit_price')
        reason = data.get('reason', 'unknown')
        logger.info(f"✅ SELL TRIGGERED → {symbol} @ {price:.2f} | Reason: {reason}")

    logger.info("Starting bar-by-bar replay...")

    for i, (ts, row) in enumerate(df.iterrows()):
        bar_data = {
            'symbol': symbol,
            'bar': {
                'ts': ts,
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            }
        }

        strategy.on_data_update({'1min': df.loc[:ts].tail(100)})

        # Force in_trade = True on every bar after first
        if symbol in state_module.states:
            state_module.states[symbol].update(in_trade=True, entry_price=row['Close'])

        stoploss_module._on_1min_bar_closed(bar_data)

        if i % 100 == 0 and symbol in stoploss_module.monitor:
            m = stoploss_module.monitor[symbol]
            logger.info(f"Bar {i:4d} | Close={row['Close']:.2f} | MaxProfit={m.get('max_profit',0):.1f}% | "
                       f"TrailFlag={m.get('trail_start_flag')} | Streak={m.get('consecutive_streak')} | "
                       f"BreachFlag={m.get('breach_flag',0)} | EffectiveSL≈{m.get('trail_stop',0):.2f}")

    # Force a sell at the end
    logger.info("Forcing final sell to test wiring...")
    stoploss_module.events.publish('exit_signal', {
        'symbol': symbol,
        'exit_price': df['Close'].iloc[-1],
        'reason': 'TEST_FORCED_SELL',
        'time': df.index[-1]
    })

    logger.info("=" * 100)
    logger.info(f"✅ TEST COMPLETED - Total bars: {len(df)} | Sells triggered: {recorded_sells}")
    logger.info("=" * 100)

if __name__ == "__main__":
    test_single_symbol()