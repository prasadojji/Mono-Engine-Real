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
DAYS_BACK = 30
TF = '5min'
QUANTITY = 900  # Units per trade for PnL calculation

def get_unique_symbols(db_path: str) -> list:
    conn = sqlite3.connect(db_path)
    query = "SELECT DISTINCT symbol FROM historical_1min"
    symbols = pd.read_sql_query(query, conn)['symbol'].tolist()
    conn.close()
    return symbols

def load_historical_from_db(symbol: str, days_back: int, db_path: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
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

def run_backtest_for_symbol(symbol: str, db_path: str, days_back: int, tf: str) -> pd.DataFrame:
    df_1min = load_historical_from_db(symbol, days_back, db_path)
    if df_1min.empty:
        print(f"No data for {symbol} — skipping.")
        return pd.DataFrame()
    
    df_5min = aggregate_to_5min(df_1min)
    if df_5min.empty:
        print(f"No 5-min candles for {symbol} after aggregation — skipping.")
        return pd.DataFrame()
    
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
        print(f"\nNo trades triggered for {symbol} during the period.")
        return pd.DataFrame()
    
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
                'Symbol': symbol,
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
            'Symbol': symbol,
            'Quantity': QUANTITY,
            'Entry Time': current_entry['timestamp'],
            'Exit Time': last_time,
            'Entry Price': current_entry['price'],
            'Exit Price': last_price,
            'PnL': pnl,
            'Cumulative PnL': cum_pnl
        })
    
    summary_df = pd.DataFrame(trade_summary)
    return summary_df

def run_backtest():
    print(f"\n=== Starting multi-symbol backtest on {TF} ({DAYS_BACK} days) ===\n")
    
    symbols = get_unique_symbols(DB_PATH)
    if not symbols:
        print("No symbols found in DB — backtest aborted.")
        return
    
    print(f"Found {len(symbols)} unique symbols in DB: {symbols}")
    
    all_summaries = []
    symbol_totals = []
    total_trades = 0
    total_pnl = 0.0
    
    for symbol in symbols:
        print(f"\n--- Backtesting {symbol} ---")
        summary_df = run_backtest_for_symbol(symbol, DB_PATH, DAYS_BACK, TF)
        if not summary_df.empty:
            print("\nTrade Summary for {symbol}:")
            print(summary_df[['Symbol', 'Quantity', 'Entry Time', 'Exit Time', 'Entry Price', 'Exit Price', 'PnL', 'Cumulative PnL']].to_string(index=False))
            num_trades = len(summary_df)
            sym_pnl = summary_df['Cumulative PnL'].iloc[-1]
            print(f"\nTrades for {symbol}: {num_trades}")
            print(f"PnL for {symbol}: {sym_pnl:.2f}")
            all_summaries.append(summary_df)
            total_trades += num_trades
            total_pnl += sym_pnl
            symbol_totals.append({
                'Symbol': symbol,
                'Total Trades': num_trades,
                'Total PnL': sym_pnl
            })
    
    if all_summaries:
        print("\n=== Overall Summary ===")
        print(f"Total Trades Across All Symbols: {total_trades}")
        print(f"Total PnL Across All Symbols: {total_pnl:.2f}")
        
        # Final PnL table per symbol
        if symbol_totals:
            totals_df = pd.DataFrame(symbol_totals)
            print("\nFinal PnL Summary Per Symbol:")
            print(totals_df.to_string(index=False))
    else:
        print("\nNo trades across any symbols.")
    
    print("\nBacktest complete.")
    
if __name__ == "__main__":
    run_backtest()