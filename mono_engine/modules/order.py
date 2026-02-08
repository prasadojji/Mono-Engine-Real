import logging

from mono_engine.modules.base import BaseModule

class Order(BaseModule):
    """
    Order module: high-level order placement, modification, cancellation.
    Supports limit, market, SL, bracket, AMO, etc.
    """

    def __init__(self, engine):
        super().__init__(engine)

    def start(self):
        logging.info("Order module starting — ready for live trading")

    def stop(self):
        logging.info("Order module stopping")

    def place_order(self, symbol, quantity, side, order_type="limit", price=None, trigger_price=0.0,
                    product="delivery", validity="day", disclosed_qty=0, amo=False, remarks="MonoEngine"):
        """
        Place a new order.
        Example: place_order("RELIANCE_EQ_NSE", 1, "buy", price=2900.0, amo=True)
        """
        if not self.session.is_logged_in():
            logging.error("Cannot place order — not logged in")
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

        try:
            resp = self.session.rest.post("/api/oms/place-order", json=payload)
            status = resp.get("s", "").lower()
            if status == "ok":
                order_id = resp.get("d", {}).get("order_id", "Unknown")
                logging.info(f"ORDER PLACED SUCCESSFULLY | ID: {order_id} | {side.upper()} {quantity} {symbol} @ {price or 'MKT'}")
            else:
                logging.error(f"ORDER REJECTED: {resp}")
            return resp
        except Exception as e:
            logging.error(f"Order placement failed: {e}")
            return None

    # Modify/cancel can be added later