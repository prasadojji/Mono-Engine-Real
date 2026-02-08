import logging
import time
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from mono_engine.config import Config
from mono_engine.core.events import EventDispatcher, EVENT_TICK, EVENT_CONNECT, EVENT_DISCONNECT, EVENT_ORDER_UPDATE, EVENT_TRADE
from mono_engine.core.session import Session
from mono_engine.core.streamer import Streamer

# Load config
config = Config.load('config.yaml')

# Session + login
session = Session(config)
two_fa = input("\nEnter FRESH 6-digit 2FA code (generate now!): ").strip()
if two_fa:
    session.config.credentials['two_fa'] = two_fa

if not session.login():
    print("Login failed — exiting")
else:
    print("*** LOGIN SUCCESSFUL — starting streamer ***")

    # Event dispatcher
    events = EventDispatcher()

    # Simple callback printers (replace with module logic later)
    def on_tick(data):
        print("TICK:", data)
    def on_connect(ev):
        print("CONNECTED:", ev)
    def on_disconnect(ev):
        print("DISCONNECTED:", ev)
    def on_order(ev):
        print("ORDER UPDATE:", ev)
    def on_trade(ev):
        print("TRADE:", ev)

    events.subscribe(EVENT_TICK, on_tick)
    events.subscribe(EVENT_CONNECT, on_connect)
    events.subscribe(EVENT_DISCONNECT, on_disconnect)
    events.subscribe(EVENT_ORDER_UPDATE, on_order)
    events.subscribe(EVENT_TRADE, on_trade)

    # Start streamer
    streamer = Streamer(session, events)
    streamer.start()

    # Subscribe to test symbols (SENSEX spot + one example if you have token)
    #test_symbols = ["-1_BSE"]  # SENSEX spot (always works)
    test_symbols = ["-1_BSE", "13_NSE"]  # SENSEX spot + RELIANCE example (token 13 is RELIANCE NSE)
# Or any option token like "12345_BFO" from your instrument master
    # Add an option token if you know one, e.g., "12345_BFO"
    streamer.subscribe_l1(test_symbols)

    print("Streamer running — watching for data (keep window open). Press Ctrl+C to stop after testing.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        streamer.stop()
        session.close()