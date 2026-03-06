#!/usr/bin/env python3
"""
Test script to verify strategy historical data preloading works correctly.
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import sqlite3
import pandas as pd
from datetime import datetime
from mono_engine.strategies.Buy_AFL_python import Buy_AFL_python

def test_strategy_preloading():
    """Test that strategy can be preloaded with historical data."""

    # Get a symbol that has historical data
    conn = sqlite3.connect('mono_engine_data.db')
    cursor = conn.cursor()

    # Find a symbol with historical data
    cursor.execute('SELECT symbol, COUNT(*) as count FROM historical_1min GROUP BY symbol ORDER BY count DESC LIMIT 1')
    result = cursor.fetchone()
    if not result:
        print("No historical data found in database")
        return False

    test_symbol = result[0]
    print(f"Testing with symbol: {test_symbol} ({result[1]} bars)")

    # Load last 50 bars for this symbol
    cursor.execute('''
        SELECT timestamp, open, high, low, close, volume
        FROM historical_1min
        WHERE symbol = ?
        ORDER BY timestamp DESC
        LIMIT 50
    ''', (test_symbol,))

    historical_bars = cursor.fetchall()
    conn.close()

    if not historical_bars:
        print(f"No historical bars found for {test_symbol}")
        return False

    print(f"Loaded {len(historical_bars)} historical bars")

    # Convert to DataFrame
    df_hist = pd.DataFrame(historical_bars,
                         columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df_hist['timestamp'] = pd.to_datetime(df_hist['timestamp'])
    df_hist = df_hist.set_index('timestamp').sort_index()

    print(f"DataFrame shape: {df_hist.shape}")
    print(f"Date range: {df_hist.index.min()} to {df_hist.index.max()}")

    # Create strategy and feed historical data
    strategy = Buy_AFL_python()
    print(f"Created strategy: {strategy.__class__.__name__}")

    # Feed historical data
    strategy.on_data_update({'1min': df_hist})
    print(f"Strategy resampled_df shape after loading: {strategy.resampled_df.shape}")

    # Check if strategy has accumulated data
    if len(strategy.resampled_df) > 0:
        print("SUCCESS: Strategy successfully preloaded with historical data!")
        print(f"   Bars accumulated: {len(strategy.resampled_df)}")
        print(f"   Last bar timestamp: {strategy.resampled_df.index[-1] if len(strategy.resampled_df) > 0 else 'None'}")

        # Test signal generation
        enter, price, reason = strategy.should_enter()
        print(f"   Signal check result: enter={enter}, price={price}, reason={reason}")

        return True
    else:
        print("❌ Strategy failed to accumulate historical data")
        return False

if __name__ == "__main__":
    success = test_strategy_preloading()
    sys.exit(0 if success else 1)