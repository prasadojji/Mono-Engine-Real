# backtest_dummy.py
"""
Clean standalone backtest runner — minimal output for testing.
Loads from DB, aggregates to 5-min, runs dummy strategy, prints only essentials.
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import talib
import numpy as np
import warnings

warnings.filterwarnings("ignore")

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from .test_dummy_strategy import DummyMacdRsiStrategy

# Config — change these as needed
DB_PATH = 'mono_engine_data.db'
SYMBOL = 'SENSEX_SPOT'  # or try 'SENSEX 26Feb26 84000 CE'
DAYS_BACK = 30
TF = '5min'
QUANTITY = 900  # Updated to 900 units per trade for PnL calculation

def load_historical_from_db(symbol: str, days_back: int) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    query = f"""
        SELECT timestamp, open, high, low, close, volume
        FROM historical_1min
        WHERE symbol = ?
        AND timestamp >= date('now', '-{days_back} days')
        ORDER BY timestamp ASC
    """
    df = pd.read_sql_query(query, conn, params=(symbol,))
    conn.close()
    
    if df.empty:
        return pd.DataFrame()
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    # Clean & force numeric
    price_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in price_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=price_cols)
    
    # Rename to capitalized for strategy consistency
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    
    return df

def aggregate_to_5min(df_1min: pd.DataFrame) -> pd.DataFrame:
    if df_1min.empty:
        return pd.DataFrame()
    
    df_5min = df_1min.resample('5min').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()
    
    # Force numeric
    df_5min = df_5min.apply(pd.to_numeric, errors='coerce').dropna()
    
    return df_5min

def run_backtest():
    print(f"\n=== Starting backtest for {SYMBOL} on {TF} ({DAYS_BACK} days) ===\n")
    
    df_1min = load_historical_from_db(SYMBOL, DAYS_BACK)
    if df_1min.empty:
        print("No data — backtest aborted.")
        return
    
    df_5min = aggregate_to_5min(df_1min)
    if df_5min.empty:
        print("No 5-min candles after aggregation — backtest aborted.")
        return
    
    strategy = DummyMacdRsiStrategy()
    
    trades = []
    min_bars_needed = max(strategy.macd_slow + strategy.macd_signal, strategy.rsi_period) + 10
    
    for i in range(min_bars_needed, len(df_5min) + 1):
        cum_5min = df_5min.iloc[:i]
        cum_1min = df_1min[df_1min.index <= cum_5min.index[-1]]
        
        strategy.on_data_update({'1min': cum_1min, '5min': cum_5min})
        
        enter, entry_price = strategy.should_enter()
        if enter:
            trades.append({
                'timestamp': cum_5min.index[-1],
                'action': 'BUY',
                'price': entry_price,
                'reason': 'MACD crossover'
            })
        
        exit_, exit_price = strategy.should_exit()
        if exit_:
            trades.append({
                'timestamp': cum_5min.index[-1],
                'action': 'SELL',
                'price': exit_price,
                'reason': 'RSI oversold'
            })
    
    if not trades:
        print("\nNo trades triggered during the period.")
    else:
        # Process trades into pairs for PnL
        trade_summary = []
        current_entry = None
        cum_pnl = 0.0
        
        for trade in trades:
            if trade['action'] == 'BUY':
                if current_entry is not None:
                    # Unclosed trade: assume exit at current price (but shouldn't happen with in_trade flag)
                    pass
                current_entry = trade
            elif trade['action'] == 'SELL':
                if current_entry is None:
                    continue
                entry_time = current_entry['timestamp']
                exit_time = trade['timestamp']
                entry_price = current_entry['price']
                exit_price = trade['price']
                pnl = (exit_price - entry_price) * QUANTITY
                cum_pnl += pnl
                trade_summary.append({
                    'Symbol': SYMBOL,
                    'Quantity': QUANTITY,
                    'Entry Time': entry_time,
                    'Exit Time': exit_time,
                    'Entry Price': entry_price,
                    'Exit Price': exit_price,
                    'PnL': pnl,
                    'Cumulative PnL': cum_pnl
                })
                current_entry = None
        
        # If open trade at end, assume exit at last close
        if current_entry is not None:
            last_time = df_5min.index[-1]
            last_price = df_5min['Close'].iloc[-1]
            pnl = (last_price - current_entry['price']) * QUANTITY
            cum_pnl += pnl
            trade_summary.append({
                'Symbol': SYMBOL,
                'Quantity': QUANTITY,
                'Entry Time': current_entry['timestamp'],
                'Exit Time': last_time,
                'Entry Price': current_entry['price'],
                'Exit Price': last_price,
                'PnL': pnl,
                'Cumulative PnL': cum_pnl
            })
        
        if trade_summary:
            summary_df = pd.DataFrame(trade_summary)
            print("\nBacktest Trade Summary (PnL per trade and cumulative):")
            print(summary_df[['Symbol', 'Quantity', 'Entry Time', 'Exit Time', 'Entry Price', 'Exit Price', 'PnL', 'Cumulative PnL']].to_string(index=False))
            print(f"\nTotal Trades: {len(trade_summary)}")
            print(f"Total PnL: {cum_pnl:.2f}")
        else:
            print("\nNo complete trades during the period.")
    
    print("\nBacktest complete.")
    
if __name__ == "__main__":
    run_backtest()