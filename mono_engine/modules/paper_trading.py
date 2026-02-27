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
# mono_engine/modules/paper_trading.py
"""
PaperTrading Module - Simulation mode only.
Now fully compatible with multi-symbol StateModule and central buy_signal handler.
"""

import logging
import time
from datetime import datetime
from typing import Optional

from .base import BaseModule
from .order import Order


class PaperTrading(Order):
    def __init__(self, engine):
        super().__init__(engine)
        self.logger = logging.getLogger(__name__)
        self.market_data = self.engine.modules.get('market_data')

    def start(self):
        super().start()
        # REMOVED: subscribe to buy_signal / sell_signal here
        # (We use the central handler in run_engine.py instead)
        self.logger.info("PaperTrading started in simulation mode (central handler active)")

    def stop(self):
        super().stop()
        self.logger.info("PaperTrading stopped")

    def place_order(self, symbol, quantity, side, order_type="limit", price=None, **kwargs):
        """Fixed for multi-symbol StateModule"""
        state = self.engine.modules['state']

        if side.lower() == 'buy':
            if state.is_in_trade(symbol):          # ← FIXED: pass symbol
                self.logger.info(f"Already in trade for {symbol} — skipping buy")
                return None
        else:  # sell
            if not state.is_in_trade(symbol):      # ← FIXED: pass symbol
                self.logger.info(f"Not in trade for {symbol} — skipping sell")
                return None

        return self._simulate_fill(symbol, side, order_type, price, quantity)

    def _simulate_fill(self, symbol: str, side: str, order_type: str, price: Optional[float] = None, quantity: int = 900, **kwargs):
        """Fixed signature + real price from MarketData"""
        real_price = self._get_real_price(symbol, price)

        order_id = f"PAPER-{int(time.time())}"
        fill_time = datetime.now()

        fill_data = {
            'order_id': order_id,
            'scrip': symbol,
            'order_type': side.lower(),
            'price': real_price,
            'quantity': quantity,
            'fill_time': fill_time,
            'buy_reason': kwargs.get('buy_reason', 'unknown') if 'kwargs' in locals() else 'unknown'  # ← add this
        }

        self.events.publish('order_filled', fill_data)
        self.logger.info(f"✅ SIMULATED {side.upper()} FILL | {quantity} {symbol} @ {real_price:.2f} | ID: {order_id}")

        return {'s': 'ok', 'd': {'order_id': order_id}}

    def _get_real_price(self, symbol: str, fallback: float = 0.0) -> float:
        if self.market_data and symbol in self.market_data.quotes:
            quote = self.market_data.quotes[symbol]
            ltp = quote.get('ltp') or quote.get('close') or fallback
            return float(ltp)
        return fallback

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

    

    def _handle_sell_signal(self, data: Dict):
        if not self.engine.modules['state'].is_in_trade():
            self.logger.warning("Not in_trade — ignoring sell signal")
            return
            
        symbol = data.get('symbol', 'UNKNOWN')
        subscribed_symbol = data.get('subscribed_symbol')
        price = data.get('price', 0.0)
        qty = data.get('quantity', PAPER_QTY)
        
        real_price = self._get_real_price(subscribed_symbol, price)
        self._simulate_fill(symbol, 'sell', 'limit', real_price)