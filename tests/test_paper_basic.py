# tests/test_paper_basic.py (Updated)
"""
Standalone test for PaperTrading module.
Simulates instantiation and method calls without full engine.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add project root to path
import time
from datetime import datetime  # For lambda in mock get_entry_details
from mono_engine.core.events import EVENT_TRADE, EVENT_ORDER_UPDATE  # Import constants (add more if needed, e.g., for 'order_update' in modify)

import logging
from mono_engine.modules.paper_trading import PaperTrading
from typing import Any
from mono_engine.core.events import EVENT_TRADE  # Import the constant (add others if needed, e.g., EVENT_ORDER_UPDATE)
#from mono_engine.core.events import EVENT_TRADE, EVENT_ORDER_UPDATE  # Import constants (add more if needed, e.g., for 'order_update' in modify)

# Mock for Session (minimal, since place_order checks is_logged_in)
class MockSession:
    def is_logged_in(self):
        return True  # Simulate logged in for paper mode (no real API)
# Mock for Streamer (minimal, no-op since not used in paper simulation)
class MockStreamer:
    def __init__(self, *args, **kwargs):
        pass  # No-op init
    def subscribe(self, *args):
        pass  # If subscribed, but not in this test

# Mock for Events
class MockEvents:
    """Simple mock for EventDispatcher to simulate publish/subscribe without real events."""
    def __init__(self):
        self.callbacks = {}  # Optional: Track for debug
    
    def subscribe(self, event_type: str, callback):
        print(f"Mock subscribe to {event_type}")
    
    def unsubscribe(self, *args):
        pass  # No-op
    
    def publish(self, event_type: str, data: Any = None):
        print(f"Mock publish: {event_type} with data {data}")

# Mock engine (with added session)
class MockEngine:
    def __init__(self):
        self.modules = {'state': MockState(), 'market_data': MockMarketData()}
        self.config = {'scrip': 'TEST_SYMBOL', 'lot_size': 50, 'retry_attempts': 3, 'retry_delay': 1}  # Dummy config (added retries for Order init)
        self.events = MockEvents()
        self.session = MockSession()  # Add this for session dependency
        self.streamer = MockStreamer()  # Add this for streamer dependency

# Mock State (with dynamic is_in_trade as lambda-supporting class)
class MockState:
    def __init__(self):
        self._in_trade = False
    
    def is_in_trade(self):
        return self._in_trade
    
    def set_in_trade(self, value: bool):
        self._in_trade = value
    
    def get_entry_details(self):
        return None  # Can enhance if needed

# Mock MarketData
class MockMarketData:
    quotes = {'TEST_SYMBOL': {'ltp': 100.50}}  # Mock real quote

# Setup logging
logging.basicConfig(level=logging.INFO)

# Instantiate and test
mock_engine = MockEngine()
paper = PaperTrading(mock_engine)

# Test place_order (buy simulation)
response = paper.place_order(symbol='TEST_SYMBOL', quantity=900, side='buy', order_type='market')
print(f"Buy Response: {response}")

# Test duplicate (mock state to True)
mock_engine.modules['state'].set_in_trade(True)
dup_response = paper.place_order(symbol='TEST_SYMBOL', quantity=900, side='buy', order_type='market')
print(f"Duplicate Buy Response: {dup_response}")  # Should be None with warning

# Test exit_order (simulate sell/exit)
paper.pending_orders['PAPER-1234567890'] = {'side': 'buy'}  # Mock pending
# Mock state entry details (namedtuple from state.py)
from collections import namedtuple
EntryDetails = namedtuple('EntryDetails', ['price', 'time', 'quantity', 'scrip'])
mock_engine.modules['state'].get_entry_details = lambda: EntryDetails(price=95.0, time=datetime.now(), quantity=900, scrip='TEST_SYMBOL')
exit_response = paper.exit_order('PAPER-1234567890')
print(f"Exit Response: {exit_response}")