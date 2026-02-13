import logging
import time

from streaming.nxtradstream import NxtradStream

from mono_engine.core.events import EventDispatcher, EVENT_TICK, EVENT_ORDER_UPDATE, EVENT_TRADE, EVENT_CONNECT, EVENT_DISCONNECT, EVENT_ERROR

class Streamer:
    def __init__(self, session, events: EventDispatcher, host: str = "api.tradejini.com"):
        self.session = session
        self.events = events
        self.host = host
        self.nx_stream: NxtradStream = None
        self.connected = False

    def _stream_callback(self, nx_stream, data):
        logging.info("Stream data received: %s", data)  # Change to info for console display
        self.events.publish(EVENT_TICK, data)

    def _connect_callback(self, nx_stream, ev):
        status = ev.get("s")
        logging.info("WS event: %s", ev)

        if status == "connected":
            self.connected = True
            nx_stream.subscribeEvents(["orders", "positions", "trades"])
            self.events.publish(EVENT_CONNECT, ev)
        elif status == "disconnected":
            self.connected = False
            self.events.publish(EVENT_DISCONNECT, ev)
            logging.warning("WS disconnected — reconnecting in 5s")
            time.sleep(5)
            self.start()
        else:
            self.events.publish(EVENT_ERROR, ev)

        if "orders" in ev:
            self.events.publish(EVENT_ORDER_UPDATE, ev)
        if "trades" in ev:
            self.events.publish(EVENT_TRADE, ev)

    def start(self) -> bool:
        if not self.session.is_logged_in():
            logging.error("Cannot start streamer — not logged in")
            return False

        apikey = self.session.config.credentials['apikey']
        access_token = self.session.rest.access_token
        auth_token = f"{apikey}:{access_token}"

        logging.info("Starting WebSocket streamer")
        self.nx_stream = NxtradStream(
            self.host,
            stream_cb=self._stream_callback,
            connect_cb=self._connect_callback
        )
        self.nx_stream.connect(auth_token)
        return True

    def subscribe_l1(self, symbols):
        if self.nx_stream and self.connected:
            self.nx_stream.subscribeL1(symbols)
            self.nx_stream.subscribeL1SnapShot(symbols)
            logging.info(f"Subscribed L1 + snapshot for: {symbols}")

    def subscribe_greeks(self, tokens):
        if self.nx_stream and self.connected:
            self.nx_stream.subscribeGreeks(tokens)
            self.nx_stream.subscribeGreeksSnapShot(tokens)
            logging.info(f"Subscribed greeks + snapshot for tokens: {tokens}")

    def subscribe_l5(self, symbols):
        if self.nx_stream and self.connected:
            self.nx_stream.subscribeL5(symbols)  # L5 for depth
            self.nx_stream.subscribeL5SnapShot(symbols)  # Snapshot
            logging.info(f"Subscribed L5 + snapshot for: {symbols}")

    def subscribe_l2(self, symbols):
        self.subscribe_l5(symbols)  # Alias l2 to l5

    def stop(self):
        if self.nx_stream:
            self.nx_stream.disconnect()
            self.connected = False
            logging.info("WebSocket streamer stopped")