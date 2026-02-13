# mono_engine/modules/paper_trading.py
"""
PaperTrading Module (New Module for Simulated Trading)

This module acts as a drop-in proxy for the Order module (Execution Engine) in paper trading mode.
It simulates order placement, fills, and exits using real market data from MarketData (ticks/quotes),
while generating dummy order IDs and publishing identical events to ensure seamless integration
with State, Portfolio, and future PnL modules. No real API calls are made.

Architectural Notes:
- Loose Coupling: Subscribes/publishes via events only (e.g., 'buy_signal', 'order_filled').
- Replaceable: Can be swapped with Order in engine.modules without affecting others.
- Event-Driven: Mirrors real execution flow by publishing EVENT_ORDER_UPDATE, EVENT_TRADE.
- Persistence: Stores simulated trades in mono_engine_data.db (trades table) for PnL analysis.
- Assumptions: Full fills only (no partials); uses latest quote for entry/exit prices.
- Extensibility: Placeholders for risk/quantity calc (Module 4 integration).
- Dependencies: events.py, market_data.py (for quotes), state.py (checks in_trade), sqlite3.

Usage:
- Loaded in run_engine.py if paper mode selected.
- Handles signals or direct calls like real Order.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Optional
import sqlite3  # For DB storage (Phase 4)

from .base import BaseModule
from .order import Order, ORDER_TYPES  # Proxy the real Order for interface compatibility

# NEW: For IST time checks
from pytz import timezone  # Add this import; if not installed, use manual UTC+5:30 offset

# Files & Cache (relative to project root or config path)
options_file = 'symbols_BSEOptions.csv'
index_file = 'symbols_Index.csv'
cache_file = 'last_sensex_open.txt'
watchlist_file = 'watchlist.json'  # New for persistence

from mono_engine.core.events import EVENT_TICK, EVENT_CONNECT, EVENT_TRADE

# Dummy order ID prefix
DUMMY_ID_PREFIX = "PAPER-"

# Hardcoded quantity for paper mode (as per user: 900; placeholder for Risk engine)
PAPER_QTY = 900

class PaperTrading(Order):  # Inherit from Order for interface compatibility
    """
    PaperTrading class: Simulates trading while using real market data.
    Overrides key methods to simulate instead of executing live.
    """
    def __init__(self, engine):
        super().__init__(engine)
        self.logger = logging.getLogger(__name__)
        self.db_conn = None  # SQLite connection (initialized in start)
        # Access MarketData module via engine for real quotes
        self.market_data = self.engine.modules.get('market_data', None)
        if not self.market_data:
            self.logger.warning("MarketData not found; simulations may lack real prices.")

    def start(self):
        """Start the module: Register event subscriptions and init DB."""
        super().start()  # Call Order's start for signal subscriptions
        self._init_db()  # Phase 4: Create/connect to DB
        self.logger.info("PaperTrading started in simulation mode.")

    def stop(self):
        """Stop the module: Close DB and unsubscribe."""
        super().stop()
        if self.db_conn:
            self.db_conn.close()
        self.logger.info("PaperTrading stopped.")

    def _init_db(self):
        """Initialize SQLite DB and create trades table if not exists."""
        # TODO: Implement in Phase 4; stubbed for now
        pass

    def _simulate_fill(self, symbol: str, side: str, order_type: str, price: Optional[float] = None):
        """
        Simulate an order fill: Get real price from MarketData, generate dummy ID,
        publish events, update state/portfolio via events, store in DB.
        """
        # Get real current price from MarketData quotes (fallback to 0 if unavailable)
        real_price = self._get_real_price(symbol)
        
        # Generate dummy order ID
        order_id = f"{DUMMY_ID_PREFIX}{int(time.time())}"
        
        # Simulate fill time
        fill_time = datetime.now()
        
        # Calculate qty (hardcoded; placeholder for Risk engine)
        qty = PAPER_QTY  # TODO: Integrate with Quantity & Risk Engine (e.g., self.engine.modules['risk'].calculate_qty(...))
        
        # Publish 'order_filled' event (mimics real streamer)
        fill_data = {
            'order_id': order_id,
            'scrip': symbol,  # Use symbol from watchlist
            'order_type': side.lower(),
            'price': real_price,
            'quantity': qty,
            'fill_time': fill_time
        }
        self.events.publish('order_filled', fill_data)
        self.events.publish(EVENT_TRADE, fill_data)  # For Portfolio
        
        # Log simulation
        self.logger.info(f"SIMULATED {side.upper()} FILL | ID: {order_id} | {qty} {symbol} @ {real_price}")
        
        # Store in DB (Phase 4 stub)
        self._store_trade(order_id, symbol, side, qty, real_price, fill_time)
        
        return {'s': 'ok', 'd': {'order_id': order_id}}  # Mimic real API response

    def _get_real_price(self, symbol: str) -> float:
        """Pull real LTP from MarketData quotes (real-time from ticks)."""
        if self.market_data and symbol in self.market_data.quotes:
            quote = self.market_data.quotes[symbol]
            ltp = quote.get('ltp', 0.0)
            logging.info(f"Real quote for {symbol}: LTP {ltp}")
            return ltp
        else:
            logging.warning(f"No real quote for {symbol}; using dummy price.")
            return 0.0  # Fallback (improve with tick subscription if needed)

    def _store_trade(self, order_id: str, symbol: str, side: str, qty: int, price: float, fill_time: datetime,
                     exit_price: Optional[float] = None, exit_time: Optional[datetime] = None, pnl: Optional[float] = None):
        """Store simulated trade in DB (Phase 4)."""
        # TODO: Implement in Phase 4
        pass

    # Overridden Methods (Proxy with Simulation)
    def place_order(self, symbol, quantity, side, order_type="limit", price=None, **kwargs):
        """Override: Simulate placement instead of real POST."""
        if not self.engine.modules['state'].is_in_trade() if side == 'buy' else self.engine.modules['state'].is_in_trade():
            return self._simulate_fill(symbol, side, order_type, price)
        else:
            self.logger.warning(f"State prevents {side} for {symbol} (in_trade: {self.engine.modules['state'].is_in_trade()})")
            return None

    def modify_order(self, order_id: str, **kwargs):
        """Override: Simulate modification (e.g., update price in pending)."""
        if order_id in self.pending_orders:
            self.pending_orders[order_id].update(kwargs)
            self.events.publish('order_update', {'order_id': order_id, **kwargs})
            self.logger.info(f"SIMULATED MODIFY | ID: {order_id}")
            return {'s': 'ok'}
        return None

    def exit_order(self, order_id: str):
        """Override: Simulate exit (sell if buy, calc PnL, update DB)."""
        if order_id in self.pending_orders:
            entry_details = self.engine.modules['state'].get_entry_details()  # From state
            if entry_details:
                exit_price = self._get_real_price(entry_details.scrip)
                exit_time = datetime.now()
                side = 'sell' if self.pending_orders[order_id]['side'] == 'buy' else 'buy'  # Assume long-only for now
                pnl = (exit_price - entry_details.price) * entry_details.quantity if side == 'sell' else 0.0  # Simple calc
                
                # Update DB with exit/PnL
                self._store_trade(order_id, entry_details.scrip, side, entry_details.quantity, 
                                  entry_details.price, entry_details.time, exit_price, exit_time, pnl)
                
                # Publish events
                self.events.publish('order_filled', {'order_id': order_id, 'order_type': side, 'price': exit_price, 
                                                     'quantity': entry_details.quantity, 'fill_time': exit_time})
                self.events.publish(EVENT_TRADE, {'pnl': pnl})  # For Portfolio
                
                del self.pending_orders[order_id]
                self.logger.info(f"SIMULATED EXIT | ID: {order_id} | PnL: {pnl}")
                return {'s': 'ok'}
        return None

    # Handle signals (inherited from Order, but add sim logging)
    def _handle_buy_signal(self, data: Dict):
        data['quantity'] = PAPER_QTY  # Override for paper
        super()._handle_buy_signal(data)  # But will call simulated place_order

    def _handle_sell_signal(self, data: Dict):
        super()._handle_sell_signal(data)