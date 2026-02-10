"""
Execution Engine Module (Module 8)

This module handles order execution: placing, modifying, exiting, and tracking updates.
Supports market, limit, SL orders for options trading (long positions).
Integrates with state.py for checks, publishes events for updates, handles partial fills/rejections/retries.
Uses Tradejini API endpoints via session/rest.
No strategy logic—pure execution.

Key Features:
- Event-driven: Reacts to buy/sell signals, publishes 'order_placed', 'order_filled', etc.
- State integration: Prevents duplicates via in_trade checks.
- Robust: Retries, partial fill accumulation.
- Extensible: Ready for bracket orders, veto from risk.py.
- Dynamic scrip: Fetches from market_data if loaded.

Dependencies:
- core/events.py for pub/sub.
- core/session.py and rest_client.py for API calls.
- state.py for position checks.
- market_data.py for scrip/token/lot (optional fallback to config).
- Config: fallback params under 'other' (scrip, lot_size, etc.).
"""


import logging

from mono_engine.modules.base import BaseModule
from typing import Dict, Optional
from time import sleep
from datetime import datetime  # For timestamps in events

# Enum-like constants for order types (extensible; map to API values)
ORDER_TYPES = {
    'MARKET': 'market',
    'LIMIT': 'limit',
    'SL': 'sl',  # Stop-loss market
    'SL_LIMIT': 'sl-limit'  # Stop-loss limit (adapt if API uses different terms)
}

class Order(BaseModule):
    """
    Order module: high-level order placement, modification, cancellation.
    Supports limit, market, SL, bracket, AMO, etc.
    """

    def __init__(self, engine):
        super().__init__(engine)
        self.logger = logging.getLogger(__name__)  # Centralized logger
        # Configurable params from engine.config (add these to your config.py if not present)
        self.scrip = self.engine.config.get('scrip', None)  # Option symbol
        self.exchange_token = self.engine.config.get('exchange_token', None)  # From scrip selection
        self.lot_size = self.engine.config.get('lot_size', 50)  # Default for NIFTY options
        self.retry_attempts = self.engine.config.get('retry_attempts', 3)  # For failed orders
        self.retry_delay = self.engine.config.get('retry_delay', 1)  # Seconds
        # In-memory tracking for pending orders (key: order_id, value: details)
        self.pending_orders: Dict[str, Dict] = {}

    def start(self):
        """Start the module: Register event subscriptions."""
        # Subscribe to signals from strategy (future module 6)
        self.events.subscribe('buy_signal', self._handle_buy_signal)
        self.events.subscribe('sell_signal', self._handle_sell_signal)
        # Subscribe to streamer for order updates
        self.events.subscribe('on_order_update', self._on_order_update)
        
        self.logger.info("OrderModule started.")

    def stop(self):
        """Stop the module: Unsubscribe events and clean up."""
        self.events.callbacks.pop('buy_signal', None)
        self.events.callbacks.pop('sell_signal', None)
        self.events.callbacks.pop('on_order_update', None)
        self.logger.info("OrderModule stopped.")

    def _handle_buy_signal(self, data: Dict):
        """
        Handle buy_signal event from module 6.
        Data: {'quantity': int, 'order_type': str (MARKET/LIMIT/SL), 'price': float (for limit/SL), ...}
        Checks state, publishes pre_order for risk veto, then places buy if approved.
        """
        if not self.scrip:
            self.logger.error("Scrip not configured. Cannot place buy order.")
            return

        state_module = self.engine.modules.get('state')
        if state_module and state_module.is_in_trade():
            self.logger.warning("Buy signal received but already in_trade. Ignoring to avoid duplicates.")
            return

        # Publish pre_order for risk veto (e.g., margin check from module 4)
        pre_data = {'action': 'buy', **data, 'scrip': self.scrip}
        self.events.publish('pre_order', pre_data)
        # Assume no veto for now (extend later to wait for 'order_veto' if needed)

        # Extract params from data and place order (adapt to your place_order)
        quantity = data.get('quantity', 1) * self.lot_size  # Adjust for lot
        order_type = ORDER_TYPES.get(data.get('order_type', 'MARKET'), 'market')
        price = data.get('price')
        trigger_price = data.get('trigger_price', 0.0) if order_type.startswith('sl') else 0.0

        resp = self.place_order(
            symbol=self.scrip,  # Use configured scrip
            quantity=quantity,
            side='buy',
            order_type=order_type,
            price=price,
            trigger_price=trigger_price,
            product='nrml',  # For options; adjust as needed
            validity='day'
        )
        if resp and resp.get('s') == 'ok':
            order_id = resp.get('d', {}).get('order_id')
            self.pending_orders[order_id] = {'side': 'buy', 'quantity': quantity, 'filled': 0}
            self.events.publish('order_placed', {'order_id': order_id, 'side': 'buy', 'scrip': self.scrip})

    def _handle_sell_signal(self, data: Dict):
        """
        Handle sell_signal event from module 6.
        Similar to buy, but checks in_trade=True.
        """
        state_module = self.engine.modules.get('state')
        if state_module and not state_module.is_in_trade():
            self.logger.warning("Sell signal received but not in_trade. Ignoring.")
            return

        pre_data = {'action': 'sell', **data, 'scrip': self.scrip}
        self.events.publish('pre_order', pre_data)

        quantity = data.get('quantity', 1) * self.lot_size
        order_type = ORDER_TYPES.get(data.get('order_type', 'MARKET'), 'market')
        price = data.get('price')
        trigger_price = data.get('trigger_price', 0.0) if order_type.startswith('sl') else 0.0

        resp = self.place_order(
            symbol=self.scrip,
            quantity=quantity,
            side='sell',
            order_type=order_type,
            price=price,
            trigger_price=trigger_price,
            product='nrml',
            validity='day'
        )
        if resp and resp.get('s') == 'ok':
            order_id = resp.get('d', {}).get('order_id')
            self.pending_orders[order_id] = {'side': 'sell', 'quantity': quantity, 'filled': 0}
            self.events.publish('order_placed', {'order_id': order_id, 'side': 'sell', 'scrip': self.scrip})

    def _on_order_update(self, data: Dict):
        """
        Handle on_order_update from streamer (normalized WS messages).
        Data: {'order_id': str, 'status': str (FILLED, PARTIAL, REJECTED, ...), 'filled_qty': int, 'price': float, 'fill_time': datetime, 'reason': str (for rejections)}
        Updates pending, handles partials, publishes 'order_filled' on complete or 'order_rejected'.
        Assumes streamer.py normalizes Shoonya WS messages into this dict format.
        """
        order_id = data.get('order_id')
        if order_id not in self.pending_orders:
            self.logger.debug(f"Ignoring update for unknown order: {order_id}")
            return

        status = data.get('status', '').upper()
        if status == 'REJECTED':
            del self.pending_orders[order_id]
            self.events.publish('order_rejected', {**data, 'scrip': self.scrip})
            self.logger.error(f"Order rejected: {order_id} Reason: {data.get('reason', 'Unknown')}")

        elif status in ['FILLED', 'PARTIAL']:
            filled_qty = data.get('filled_qty', 0)
            self.pending_orders[order_id]['filled'] += filled_qty

            remaining = self.pending_orders[order_id]['quantity'] - self.pending_orders[order_id]['filled']
            if remaining <= 0:
                # Complete fill
                fill_data = {
                    'order_type': self.pending_orders[order_id]['side'],
                    'scrip': self.scrip,
                    'price': data.get('price'),
                    'quantity': self.pending_orders[order_id]['filled'] // self.lot_size,  # User-level qty
                    'fill_time': data.get('fill_time', datetime.now())
                }
                self.events.publish('order_filled', fill_data)
                del self.pending_orders[order_id]
                self.logger.info(f"Order fully filled: {order_id}")
            else:
                # Partial: Log and wait for more updates
                self.logger.info(f"Partial fill: {order_id} Filled {self.pending_orders[order_id]['filled']} / {self.pending_orders[order_id]['quantity']}")

        else:
            self.logger.warning(f"Unknown order status: {status} for {order_id}")

    def modify_order(self, order_id: str, new_price: Optional[float] = None, new_quantity: Optional[int] = None, new_trigger_price: Optional[float] = None):
        """
        Modify an existing order (e.g., for trailing SL).
        Uses Tradejini API endpoint for modification.
        """
        if order_id not in self.pending_orders:
            self.logger.error(f"Cannot modify unknown order: {order_id}")
            return None

        payload = {
            "order_id": order_id
        }
        if new_price is not None:
            payload["price"] = new_price
        if new_quantity is not None:
            payload["qty"] = new_quantity * self.lot_size  # Adjust for lot
        if new_trigger_price is not None:
            payload["trigPrice"] = new_trigger_price

        try:
            resp = self.session.rest.post("/api/oms/modify-order", json=payload)  # Adapt endpoint if different
            status = resp.get("s", "").lower()
            if status == "ok":
                self.logger.info(f"ORDER MODIFIED SUCCESSFULLY | ID: {order_id}")
                # Update pending if quantity changed
                if new_quantity:
                    self.pending_orders[order_id]['quantity'] = new_quantity * self.lot_size
                return resp
            else:
                self.logger.error(f"ORDER MODIFY REJECTED: {resp}")
                return None
        except Exception as e:
            self.logger.error(f"Modify failed: {e}")
            return None

    def exit_order(self, order_id: str):
        """
        Cancel/exit an order.
        Uses Tradejini API endpoint for cancellation.
        """
        try:
            payload = {"order_id": order_id}
            resp = self.session.rest.post("/api/oms/cancel-order", json=payload)  # Adapt endpoint if different
            status = resp.get("s", "").lower()
            if status == "ok":
                if order_id in self.pending_orders:
                    del self.pending_orders[order_id]
                self.logger.info(f"ORDER CANCELED SUCCESSFULLY | ID: {order_id}")
                self.events.publish('order_canceled', {'order_id': order_id, 'scrip': self.scrip})
                return resp
            else:
                self.logger.error(f"ORDER CANCEL REJECTED: {resp}")
                return None
        except Exception as e:
            self.logger.error(f"Cancel failed: {e}")
            return None   

    def place_order(self, symbol, quantity, side, order_type="limit", price=None, trigger_price=0.0,
                    product="delivery", validity="day", disclosed_qty=0, amo=False, remarks="MonoEngine"):
        """
        Place a new order.
        Example: place_order("RELIANCE_EQ_NSE", 1, "buy", price=2900.0, amo=True)
        """
        if not self.session.is_logged_in():
            self.logger.error("Cannot place order — not logged in")
            return None

        payload = {
            "sym": symbol,
            "qty": quantity,
            "side": side.lower(),
            "type": order_type.lower(),
            "product": product.lower(),
            "validity": validity.lower(),
            "disclosedQty": disclosed_qty,
            "amo": "yes" if amo else "no",
            "remarks": remarks
        }
        if price is not None:
            payload["price"] = price
        if trigger_price:
            payload["trigPrice"] = trigger_price

        for attempt in range(1, self.retry_attempts + 1):
            try:
                resp = self.session.rest.post("/api/oms/place-order", json=payload)
                status = resp.get("s", "").lower()
                if status == "ok":
                    order_id = resp.get("d", {}).get('order_id', "Unknown")
                    self.logger.info(f"ORDER PLACED SUCCESSFULLY | ID: {order_id} | {side.upper()} {quantity} {symbol} @ {price or 'MKT'}")
                    return resp
                else:
                    self.logger.error(f"ORDER REJECTED on attempt {attempt}: {resp}")
            except Exception as e:
                self.logger.error(f"Order placement failed on attempt {attempt}: {e}")

            if attempt < self.retry_attempts:
                self.logger.info(f"Retrying in {self.retry_delay} seconds...")
                sleep(self.retry_delay)

        self.logger.error(f"Order placement failed after {self.retry_attempts} attempts.")
        return None

# Future extensions:
# - Add bracket orders (entry + SL + target).
# - Handle 'order_veto' from risk.py: Subscribe and cancel if vetoed.
# self.events.subscribe('order_veto', self._handle_veto)
# def _handle_veto(self, data):
#     order_id = data.get('order_id')
#     if order_id in self.pending_orders:
#         self.exit_order(order_id)
#         self.logger.warning(f"Order vetoed by risk: {order_id}")