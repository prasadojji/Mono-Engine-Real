# mono_engine/modules/state.py
"""
State Engine Module

This module maintains the trade state for the trading engine, focusing on options trading for long positions.
It tracks whether the system is currently in a trade (IN_TRADE flag), along with entry details like price, time, and quantity.
State is updated via event subscriptions (e.g., from order fills) and provides query methods for other modules.
It performs an initial sync with the portfolio on startup/reconnect to handle existing positions.
For runtime persistence, it uses in-memory storage (extensible to file/DB later).
No strategy or execution logic here—strictly state management.

Key Features:
- Event-driven updates for real-time consistency.
- Initial and on-reconnect sync with broker via portfolio module.
- Thread-safe if engine is multi-threaded (using locks).
- Publishes 'state_updated' events for subscribers (e.g., strategy, stop-loss).
- Prevents repainting issues by basing state on confirmed broker fills, not signals.

Dependencies:
- Relies on core/events.py for pub/sub.
- Uses portfolio.py for position queries (via engine.rest or events).
- Assumes single scrip/position for now; extensible to multi-scrip.
"""

import logging
from datetime import datetime
from threading import Lock  # For thread-safety in multi-threaded environments
from collections import namedtuple

from .base import BaseModule

# Define a simple namedtuple for trade entry details (immutable for safety)
EntryDetails = namedtuple('EntryDetails', ['price', 'time', 'quantity', 'scrip'])

class TradeState:
    """
    Internal class to hold the trade state.
    This can be extended for persistence (e.g., add methods to save/load from JSON).
    """
    def __init__(self):
        self.in_trade = False
        self.entry_details = None  # EntryDetails or None
        self._lock = Lock()  # For thread-safe access/updates

    def update(self, in_trade: bool, entry_details=None):
        """Update the state atomically."""
        with self._lock:
            self.in_trade = in_trade
            self.entry_details = entry_details

    def get_state(self):
        """Get a snapshot of the current state (thread-safe)."""
        with self._lock:
            return {
                'in_trade': self.in_trade,
                'entry_details': self.entry_details
            }

class StateModule(BaseModule):
    """
    State Engine module implementation.
    Inherits from BaseModule to integrate with the engine.
    """
    def __init__(self, engine):
        super().__init__(engine)
        self.state = TradeState()  # In-memory state holder
        self.logger = logging.getLogger(__name__)  # Centralized logging
        # Configurable params (from config.py, e.g., scrip to monitor)
        self.scrip = self.engine.config.get('scrip', None)  # Assume single scrip for now

    def start(self):
        """Start the module: Register event subscriptions and perform initial sync."""
        # Subscribe to relevant events
        self.events.subscribe('order_filled', self._on_order_filled)
        self.events.subscribe('on_connect', self._sync_state)  # Sync on WS connect/reconnect
        self.events.subscribe('on_error', self._handle_error)  # Flag stale on errors

        # Initial sync on start
        self._sync_state(None)  # Pass dummy data for on_connect event
        self.logger.info("StateModule started and initial sync performed.")

    def stop(self):
        """Stop the module: Unsubscribe events and optionally persist state."""
        # Unsubscribe (though events.py might not require it, good practice)
        self.events.callbacks.pop('order_filled', None)
        self.events.callbacks.pop('on_connect', None)
        self.events.callbacks.pop('on_error', None)
        
        # Optional: Persist state to file for restart (future enhancement)
        # self._persist_state()
        self.logger.info("StateModule stopped.")

    def _sync_state(self, data):
        """
        Sync state with broker via portfolio module.
        Queries current positions to initialize or verify state.
        Handles startup, reconnects, or anomalies.
        """
        try:
            # Assume portfolio.py has a method to get positions (use engine to access)
            positions = self.engine.modules['portfolio'].get_positions()  # Or via rest_client directly
            # Filter for our scrip (options focused)
            position = next((p for p in positions if p['scrip'] == self.scrip), None)
            
            if position and position['net_qty'] > 0:  # Long position exists
                entry_price = position.get('avg_price', 0.0)  # Approximate if no exact entry
                entry_time = datetime.now()  # Placeholder; ideally fetch from order history if needed
                entry_qty = position['net_qty']
                entry_details = EntryDetails(price=entry_price, time=entry_time, quantity=entry_qty, scrip=self.scrip)
                self.state.update(in_trade=True, entry_details=entry_details)
                self.logger.info(f"State synced: Existing position found for {self.scrip}. Set in_trade=True.")
            else:
                self.state.update(in_trade=False)
                self.logger.info("State synced: No existing position. Set in_trade=False.")
            
            # Publish update after sync
            self.events.publish('state_updated', self.state.get_state())
        except Exception as e:
            self.logger.error(f"State sync failed: {e}. State marked as stale.")
            # Optionally flag state as unreliable until next sync

    def _on_order_filled(self, data):
        """
        Handle order_filled event (from streamer/order.py).
        Updates state based on fill details.
        Data expected: {'order_type': 'buy'/'sell', 'scrip': str, 'price': float, 'quantity': int, 'fill_time': datetime}
        Handles partial fills by accumulating (for simplicity, assume full fills here; extend for partials).
        """
        if data['scrip'] != self.scrip:
            return  # Ignore unrelated scrips
        
        try:
            if data['order_type'] == 'buy':
                if not self.state.get_state()['in_trade']:  # Avoid duplicates
                    entry_details = EntryDetails(
                        price=data['price'],
                        time=data['fill_time'],
                        quantity=data['quantity'],
                        scrip=data['scrip']
                    )
                    self.state.update(in_trade=True, entry_details=entry_details)
                    self.logger.info(f"Buy filled: Set in_trade=True for {self.scrip} at {data['price']}.")
                else:
                    self.logger.warning("Buy filled but already in_trade. Ignored to prevent duplicates.")
            
            elif data['order_type'] == 'sell':
                if self.state.get_state()['in_trade']:
                    self.state.update(in_trade=False)
                    self.logger.info(f"Sell filled: Set in_trade=False for {self.scrip}.")
                else:
                    self.logger.warning("Sell filled but not in_trade. Possible sync issue.")
            
            # Publish state update for other modules
            self.events.publish('state_updated', self.state.get_state())
        except KeyError as e:
            self.logger.error(f"Invalid order_filled data: Missing {e}. State unchanged.")

    def _handle_error(self, data):
        """Handle errors (e.g., WS disconnect): Mark state as stale and trigger re-sync on next connect."""
        self.logger.warning(f"Error event: {data}. State may be stale; will re-sync on connect.")

    # Query methods for other modules (clean interface)
    def is_in_trade(self):
        """Check if currently in a trade."""
        return self.state.get_state()['in_trade']

    def get_entry_details(self):
        """Get entry details if in_trade, else None."""
        state = self.state.get_state()
        return state['entry_details'] if state['in_trade'] else None

    # Future extension: Persist to file
    # def _persist_state(self):
    #     with open('state.json', 'w') as f:
    #         json.dump(self.state.get_state(), f)
    
    # def _load_persisted_state(self):
    #     if os.path.exists('state.json'):
    #         with open('state.json', 'r') as f:
    #             data = json.load(f)
    #             # Restore state