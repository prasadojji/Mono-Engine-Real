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
"""
State Engine - Multi-symbol, thread-safe, event-driven.
No strategy/execution logic here.
"""

import logging
from datetime import datetime
from threading import Lock
from collections import defaultdict, namedtuple

from .base import BaseModule

EntryDetails = namedtuple('EntryDetails', ['price', 'time', 'quantity', 'scrip'])

class TradeState:
    def __init__(self):
        self.in_trade = False
        self.entry_details = None
        self.trade_history = []
        self._lock = Lock()

    def update(self, in_trade: bool, entry_details=None):
        with self._lock:
            self.in_trade = in_trade
            self.entry_details = entry_details

    def get_state(self):
        with self._lock:
            return {'in_trade': self.in_trade, 'entry_details': self.entry_details}


class StateModule(BaseModule):
    def __init__(self, engine):
        super().__init__(engine)
        self.states = defaultdict(TradeState)   # symbol -> TradeState
        self.logger = logging.getLogger(__name__)

    def start(self):
        self.events.subscribe('order_filled', self._on_order_filled)
        self.events.subscribe('on_connect', self._sync_state)
        self.events.subscribe('on_error', self._handle_error)
        self._sync_state(None)
        self.logger.info("StateModule started (multi-symbol ready)")

    def stop(self):
        self.events.unsubscribe('order_filled', self._on_order_filled)
        self.events.unsubscribe('on_connect', self._sync_state)
        self.events.unsubscribe('on_error', self._handle_error)
        self.logger.info("StateModule stopped")

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

                        # === NEW: Publish trade_entered for StoplossModule (exact location you asked) ===
                        self.events.publish('trade_entered', {
                            'symbol': sym,           # standard key used by MarketData/Strategy/Stoploss
                            'scrip': sym,            # keep your original key for safety
                            'entry_price': data['price'],
                            'quantity': data['quantity'],
                            'fill_time': data.get('fill_time', datetime.now())
                        })

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
    def is_in_trade(self, symbol: str) -> bool:
        """MUST pass symbol (e.g. '842710_BFO' or '-51_BSE')"""
        if not symbol:
            self.logger.warning("is_in_trade called without symbol - returning False")
            return False
        return self.states[symbol].get_state()['in_trade']

    def get_entry_details(self, symbol: str):
        if not symbol:
            return None
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