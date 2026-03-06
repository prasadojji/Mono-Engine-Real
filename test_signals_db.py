#!/usr/bin/env python3
"""
Test script to verify real-time signal publishing
"""

import sys
import os
sys.path.append('.')

from datetime import datetime
import sqlite3

# Mock engine for testing
class MockEngine:
    def __init__(self):
        self.modules = {}
        self.events = MockEvents()
        self.session = None
        self.config = {}
        self.logger = None

class MockEvents:
    def subscribe(self, event, handler): pass
    def unsubscribe(self, event, handler): pass

def test_pnl_signals():
    """Test if PnL module creates trades_signals table and publishes signals"""

    print("Testing PnL signal publishing...")

    # Import and initialize PnL module
    from mono_engine.modules.pnl import PnLModule
    mock_engine = MockEngine()
    pnl = PnLModule(mock_engine)

    # Check if table was created
    conn = sqlite3.connect('mono_engine_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="trades_signals"')
    table_exists = cursor.fetchone()
    print(f"trades_signals table exists: {table_exists is not None}")

    if table_exists:
        # Check table structure
        cursor.execute('PRAGMA table_info(trades_signals)')
        columns = cursor.fetchall()
        print(f"Table has {len(columns)} columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

        # Test publishing a signal
        print("\nTesting signal publishing...")
        signal_data = {
            'signal_id': 'test_buy_signal_123',
            'trade_id': None,
            'symbol': 'TEST_SYMBOL',
            'signal_type': 'buy',
            'signal_reason': 'TEST_BREAKOUT',
            'signal_price': 100.50,
            'candle_close': None,
            'next_candle_direction': None,
            'signal_time': datetime.now(),
            'fill_price': None,
            'fill_time': None,
            'realized_pnl': None,
            'is_live': 1,
            'status': 'signaled'
        }

        pnl._publish_signal_to_db(signal_data)
        print("Signal published to database")

        # Check if signal was inserted
        cursor.execute('SELECT COUNT(*) FROM trades_signals WHERE signal_id = ?', ('test_buy_signal_123',))
        count = cursor.fetchone()[0]
        print(f"Signal found in database: {count > 0}")

        if count > 0:
            cursor.execute('SELECT * FROM trades_signals WHERE signal_id = ?', ('test_buy_signal_123',))
            record = cursor.fetchone()
            print("Signal record:", record)

    conn.close()

if __name__ == '__main__':
    test_pnl_signals()