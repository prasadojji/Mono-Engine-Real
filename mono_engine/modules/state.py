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
- Now supports multi-symbol (per scrip from watchlist).
"""

import logging
from datetime import datetime
from threading import Lock  # For thread-safety in multi-threaded environments
from collections import namedtuple, defaultdict  # Added defaultdict for multi-symbol

from .base import BaseModule

# Define a simple namedtuple for trade entry details (immutable for safety)
EntryDetails = namedtuple('EntryDetails', ['price', 'time', 'quantity', 'scrip'])

class TradeState:
    """
    Internal class to hold the trade state for a single symbol.
    This can be extended for persistence (e.g., add methods to save/load from JSON).
    """
    def __init__(self):
        self.in_trade = False
        self.entry_details = None  # EntryDetails or None
        self._lock = Lock()  # For thread-safe access/updates
        self.trade_history = []  # NEW: List of completed trades
        
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
    Now supports multi-symbol states via defaultdict.
    """
    def __init__(self, engine):
        super().__init__(engine)
        self.states = defaultdict(TradeState)  # Per-symbol states (auto-creates on access)
        self.logger = logging.getLogger(__name__)  # Centralized logging
        # Configurable params (from config.py, e.g., default scrip if no symbol passed)
        self.default_scrip = self.engine.config.get('scrip', None)  # For backward compat

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
        Queries current positions to initialize or verify per-symbol states.
        """
        try:
            # Assume portfolio module has get_positions() returning list of dicts with 'scrip', 'net_qty', etc.
            positions = self.engine.modules['portfolio'].get_positions()
            synced_symbols = set()
            for position in positions:
                sym = position['scrip']
                synced_symbols.add(sym)
                if position['net_qty'] > 0:  # Long position
                    entry_price = position.get('avg_price', 0.0)  # Approximate if no exact entry
                    entry_time = datetime.now()  # Placeholder; ideally fetch from order history if needed
                    entry_qty = position['net_qty']
                    entry_details = EntryDetails(price=entry_price, time=entry_time, quantity=entry_qty, scrip=sym)
                    self.states[sym].update(in_trade=True, entry_details=entry_details)
                    self.logger.info(f"State synced: Existing position found for {sym}. Set in_trade=True.")
                else:
                    self.states[sym].update(in_trade=False)
                    self.logger.info(f"State synced: No position for {sym}. Set in_trade=False.")
            
            # For any active states not in positions, reset (safety)
            for sym in list(self.states.keys()):
                if sym not in synced_symbols:
                    self.states[sym].update(in_trade=False)
                    self.logger.warning(f"Reset stale state for {sym} not in current positions.")
            
            # Publish update after sync (per-symbol or all)
            self.events.publish('state_updated', {sym: self.states[sym].get_state() for sym in self.states})
        except Exception as e:
            self.logger.error(f"State sync failed: {e}. States may be stale.")

    def _on_order_filled(self, data):
        """Handle confirmed fill events from execution. Updates state based on fill details."""
        sym = data.get('scrip')
        if not sym:
            self.logger.warning("order_filled missing scrip—ignored.")
            return
        
        try:
            order_type = data['order_type']
            if order_type == 'buy':
                if not self.states[sym].get_state()['in_trade']:  # Avoid duplicates
                    entry_details = EntryDetails(
                        price=data['price'],
                        time=data['fill_time'],
                        quantity=data['quantity'],
                        scrip=sym
                    )
                    self.states[sym].update(in_trade=True, entry_details=entry_details)
                    self.logger.info(f"Buy filled: Set in_trade=True for {sym} at {data['price']}.")
                else:
                    self.logger.warning(f"Buy filled but already in_trade for {sym}. Ignored.")
            
            elif order_type == 'sell':
                if self.states[sym].get_state()['in_trade']:
                    entry = self.states[sym].entry_details
                    exit_time = data.get('fill_time', datetime.now())
                    exit_price = data['price']

                    trade = {
                        "entry_time": entry.time,
                        "entry_price": entry.price,
                        "exit_time": exit_time,
                        "exit_price": exit_price
                    }
                    self.states[sym].trade_history.append(trade)  # Record completed trade

                    self.states[sym].update(in_trade=False)
                    self.logger.info(f"Sell filled: Set in_trade=False for {sym}. Trade recorded.")
                else:
                    self.logger.warning(f"Sell filled but not in_trade for {sym}. Possible sync issue.")
            
            # Publish state update for this symbol
            self.events.publish('state_updated', {sym: self.states[sym].get_state()})
        except KeyError as e:
            self.logger.error(f"Invalid order_filled data for {sym}: Missing {e}. State unchanged.")

    def _handle_error(self, data):
        """Handle errors (e.g., WS disconnect): Mark state as stale and trigger re-sync on next connect."""
        self.logger.warning(f"Error event: {data}. States may be stale; will re-sync on connect.")

    # Query methods for other modules (now require symbol)
    def is_in_trade(self, symbol):
        """Check if currently in a trade for the symbol."""
        return self.states[symbol].get_state()['in_trade']

    def get_entry_details(self, symbol):
        """Get entry details if in_trade for the symbol, else None."""
        state = self.states[symbol].get_state()
        return state['entry_details'] if state['in_trade'] else None

    # Future extension: Persist to file
    # def _persist_state(self):
    #     with open('state.json', 'w') as f:
    #         json.dump({sym: s.get_state() for sym, s in self.states.items()}, f)
    
    # def _load_persisted_state(self):
    #     if os.path.exists('state.json'):
    #         with open('state.json', 'r') as f:
    #             data = json.load(f)
    #             for sym, state_data in data.items():
    #                 # Restore per-symbol