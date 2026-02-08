import logging
from collections import defaultdict

from mono_engine.modules.base import BaseModule
from mono_engine.core.events import EVENT_CONNECT, EVENT_ORDER_UPDATE, EVENT_TRADE

class Portfolio(BaseModule):
    """
    Portfolio module: tracks positions, funds, real-time P&L from events + initial REST poll.
    """

    def __init__(self, engine):
        super().__init__(engine)
        self.positions = {}  # netQty, avgPrice, unrealizedPnl, etc. by symbol
        self.funds = {}      # availCash, availMargin, etc.

    def start(self):
        logging.info("Portfolio module starting — subscribing to updates")
        self.events.subscribe(EVENT_CONNECT, self._on_connect)
        self.events.subscribe(EVENT_ORDER_UPDATE, self._on_order_update)
        self.events.subscribe(EVENT_TRADE, self._on_trade_update)

    def stop(self):
        logging.info("Portfolio module stopping")
        self.events.unsubscribe(EVENT_CONNECT, self._on_connect)
        self.events.unsubscribe(EVENT_ORDER_UPDATE, self._on_order_update)
        self.events.unsubscribe(EVENT_TRADE, self._on_trade_update)

    def _on_connect(self, data):
        logging.info("Portfolio: WS connected — fetching initial positions/funds")
        self._fetch_positions()
        self._fetch_funds()

    def _on_order_update(self, data):
        logging.info(f"ORDER UPDATE: {data}")
        # Parse order status changes (filled, cancelled, etc.) — update positions if needed
        # Tradejini events have order details — extend parsing as needed

    def _on_trade_update(self, data):
        logging.info(f"TRADE EXECUTED: {data}")
        # Update positions/P&L on new trades
        self._fetch_positions()  # Simple refresh — or parse event for delta

    def _fetch_positions(self):
        try:
            resp = self.session.rest.get("/api/oms/positions")
            positions_data = resp.get("d", [])
            total_unreal = 0.0
            logging.info(f"POSITIONS ({len(positions_data)} open):")
            for pos in positions_data:
                sym = pos.get("symId", "Unknown")
                net = pos.get("netQty", 0)
                avg = pos.get("avgPrice", 0.0)
                unreal = pos.get("unrealizedPnl", 0.0)
                logging.info(f"  {sym} | Net: {net} | Avg: {avg:.2f} | Unreal P&L: {unreal:+.2f}")
                total_unreal += unreal
                self.positions[sym] = pos
            logging.info(f"Total Unrealized P&L: {total_unreal:+.2f}")
        except Exception as e:
            logging.error(f"Failed to fetch positions: {e}")

    def _fetch_funds(self):
        try:
            resp = self.session.rest.get("/api/oms/limits")
            funds_data = resp.get("d", {})
            avail_cash = funds_data.get("availCash", 0.0)
            avail_margin = funds_data.get("availMargin", 0.0)
            used_margin = funds_data.get("marginUsed", 0.0)
            logging.info(f"FUNDS: Cash ₹{avail_cash:,.2f} | Margin ₹{avail_margin:,.2f} | Used ₹{used_margin:,.2f}")
            self.funds = funds_data
        except Exception as e:
            logging.error(f"Failed to fetch funds: {e}")