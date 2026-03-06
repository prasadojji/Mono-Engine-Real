#!/usr/bin/env python3
"""
Test script for 2% profit stoploss strategy
Tests the new Stoploss2PercentModule independently
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mono_engine.modules.stoploss_2percent import Stoploss2PercentModule


class MockEngine:
    """Mock engine for testing"""
    def __init__(self):
        self.config = {
            'stoploss_params': {
                'post_exit_monitoring_minutes': 60
            }
        }
        self.modules = {
            'state': MockStateModule()
        }
        self.session = None  # Not needed for stoploss testing
        self.streamer = None  # Not needed for stoploss testing
        self.events = None  # Will be set by test


class MockStateModule:
    """Mock state module"""
    def __init__(self):
        self.trades = {}  # symbol -> trade info

    def is_in_trade(self, symbol):
        return symbol in self.trades

    def get_entry_details(self, symbol):
        if symbol in self.trades:
            return MockEntryDetails(self.trades[symbol])
        return None


class MockEntryDetails:
    """Mock entry details"""
    def __init__(self, trade_info):
        self.quantity = trade_info.get('quantity', 45)
        self.entry_price = trade_info.get('entry_price', 0)


class MockEventDispatcher:
    """Mock event dispatcher"""
    def __init__(self):
        self.subscriptions = {}

    def subscribe(self, event, callback):
        if event not in self.subscriptions:
            self.subscriptions[event] = []
        self.subscriptions[event].append(callback)

    def unsubscribe(self, event, callback):
        if event in self.subscriptions:
            self.subscriptions[event].remove(callback)

    def publish(self, event, data):
        if event in self.subscriptions:
            for callback in self.subscriptions[event]:
                callback(data)


def create_test_data():
    """Create sample price data for testing"""
    # Create a price series that goes up 3% then down 3%
    base_price = 100.0
    timestamps = pd.date_range('2024-01-01 09:15:00', periods=20, freq='1min')

    # Price movement: start at 100, go up to 103 (3%), then down to 97 (3% drop from high)
    prices = []
    for i in range(20):
        if i < 10:
            # Go up to 103
            price = base_price + (i * 0.3)
        else:
            # Go down from 103 to 97
            price = 103.0 - ((i - 10) * 0.6)
        prices.append(price)

    df = pd.DataFrame({
        'timestamp': timestamps,
        'open': prices,
        'high': [p + 0.1 for p in prices],  # Slightly higher highs
        'low': [p - 0.1 for p in prices],   # Slightly lower lows
        'close': prices,
        'volume': [1000] * 20
    })

    return df


def test_2percent_stoploss():
    """Test the 2% profit stoploss strategy"""
    print("Testing 2% Profit Stoploss Strategy")
    print("=" * 50)

    # Setup
    mock_engine = MockEngine()
    mock_engine.events = MockEventDispatcher()
    stoploss = Stoploss2PercentModule(mock_engine)
    stoploss.start()

    # Mock state module
    mock_engine.modules['state'].trades['TEST_SYMBOL_BFO'] = {
        'quantity': 45,
        'entry_price': 100.0
    }

    # Test data
    test_df = create_test_data()
    print(f"Test data: {len(test_df)} bars")
    print(".1f")
    print(".1f")
    print()

    exit_signals = []

    # Mock exit signal handler
    def on_exit_signal(data):
        exit_signals.append(data)
        print(f"EXIT SIGNAL: {data}")

    mock_engine.events.subscribe('exit_signal', on_exit_signal)

    # Start monitoring
    stoploss._on_trade_entered({
        'symbol': 'TEST_SYMBOL_BFO',
        'entry_price': 100.0
    })

    # Feed bars one by one
    for idx, row in test_df.iterrows():
        bar_data = {
            'symbol': 'TEST_SYMBOL_BFO',
            'bar': {
                'ts': row['timestamp'],
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': int(row['volume'])
            }
        }

        stoploss._on_1min_bar_closed(bar_data)

        # Check if exit was triggered
        if exit_signals:
            break

    # Results
    print("\nTest Results:")
    print(f"Exit signals generated: {len(exit_signals)}")

    if exit_signals:
        signal = exit_signals[0]
        print(f"Exit reason: {signal['reason']}")
        print(".2f")
        print(".2f")
        print(".1f")
        print(".2f")

        # Verify it exited with some profit (strategy trails from high)
        entry = 100.0
        exit_price = signal['exit_price']
        highest_price = signal['highest_price']
        profit_pct = (exit_price - entry) / entry * 100
        max_profit_pct = signal['max_profit_pct']

        print(".1f")
        print(".1f")

        # Strategy should exit when price drops 2% below highest achieved after 2% target
        trail_level = highest_price * 0.98
        print(".2f")

        if exit_price <= trail_level and max_profit_pct >= 2.0:
            print("SUCCESS: Exited correctly when price dropped below trail level")
        else:
            print("FAILED: Exit condition not met correctly")
    else:
        print("FAILED: No exit signal generated")

    stoploss.stop()
    return len(exit_signals) > 0


if __name__ == "__main__":
    success = test_2percent_stoploss()
    sys.exit(0 if success else 1)