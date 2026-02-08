import logging
from typing import List

from streaming.nxtradstream import NxtradStream  # Direct import from your repo's streaming folder

from mono_engine.core.events import EventDispatcher, EVENT_TICK, EVENT_ORDER_UPDATE, EVENT_TRADE, EVENT_CONNECT, EVENT_DISCONNECT, EVENT_ERROR

class Streamer:
    """
    Thin wrapper around NxtradStream for real-time WebSocket data.
    Integrates with Session (auth_token) and EventDispatcher (normalized events).
    """

    def __init__(self, session, events: EventDispatcher, host: str = "api.tradejini.com"):
        self.session = session
        self.events = events
        self.host = host
        self.nx_stream: NxtradStream = None
        self.connected = False

    def _stream_callback(self, nx_stream, data):
        """Normalize and publish tick/quote data"""
        # data is dict from binary protocol — publish raw for now, modules can parse
        logging.debug("Stream data received: {}", data)
        self.events.publish(EVENT_TICK, data)

    def _connect_callback(self, nx_stream, ev):
        """Handle connection events and auto-subscribe defaults"""
        status = ev.get("s")
        logging.info("WS event: {}", ev)

        if status == "connected":
            self.connected = True
            # Auto-subscribe to order/trade/position updates (as in your old project)
            nx_stream.subscribeEvents(["orders", "positions", "trades"])
            self.events.publish(EVENT_CONNECT, ev)
        elif status == "disconnected":
            self.connected = False
            self.events.publish(EVENT_DISCONNECT, ev)
            # Simple reconnect attempt
            logging.warning("WS disconnected — attempting reconnect in 5s")
            time.sleep(5)
            self.start()
        else:
            self.events.publish(EVENT_ERROR, ev)

        # Publish order/trade updates specifically
        if "orders" in ev:
            self.events.publish(EVENT_ORDER_UPDATE, ev)
        if "trades" in ev:
            self.events.publish(EVENT_TRADE, ev)

    def start(self) -> bool:
        """Start WebSocket connection using session auth_token"""
        if not self.session.is_logged_in():
            logging.error("Cannot start streamer — session not logged in")
            return False

        apikey = self.session.config.credentials['apikey']
        access_token = self.session.rest.access_token
        auth_token = f"{apikey}:{access_token}"

        logging.info("Starting WebSocket streamer with auth_token")

        self.nx_stream = NxtradStream(
            self.host,
            stream_cb=self._stream_callback,
            connect_cb=self._connect_callback
        )
        self.nx_stream.connect(auth_token)
        return True

    def subscribe_l1(self, symbols: List[str]):
        """Subscribe to L1 quotes for symbols (e.g., ['12345_BFO'])"""
        if self.nx_stream and self.connected:
            self.nx_stream.subscribeL1(symbols)
            self.nx_stream.subscribeL1SnapShot(symbols)  # Initial snapshot
            logging.info("Subscribed to L1 for: {}", symbols)

    def stop(self):
        if self.nx_stream:
            self.nx_stream.disconnect()
            self.connected = False
            logging.info("WebSocket streamer stopped")

    def close(self):
        self.stop()