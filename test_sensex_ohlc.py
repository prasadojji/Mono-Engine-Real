import logging
import os
import time
import json
from tabulate import tabulate

from mono_engine.config import Config
from mono_engine.core.session import Session
from mono_engine.core.events import EventDispatcher, EVENT_TICK
from mono_engine.core.streamer import Streamer

CACHE_FILE = "sensex_ohlc_cache.json"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

config = Config.load('config.yaml')
session = Session(config)

two_fa = input("\nEnter FRESH 6-digit 2FA code (generate now!): ").strip()
if two_fa:
    session.config.credentials['two_fa'] = two_fa

if not session.login():
    print("Login failed — exiting")
else:
    print("LOGIN SUCCESSFUL — starting streamer for SENSEX OHLC")

    events = EventDispatcher()
    streamer = Streamer(session, events)

    # Load cache
    cached_ohlc = None
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
            cached_ohlc = cache.get("ohlc")
            cached_date = cache.get("date")
            logging.info(f"Loaded cached SENSEX OHLC from {cached_date}: {cached_ohlc}")

    # Callback for ticks
    def on_tick(data):
        if data.get("symbol") == "-1_BSE":
            q = data
            current_ohlc = {
                "open": q.get("open"),
                "high": q.get("high"),
                "low": q.get("low"),
                "close": q.get("close"),
                "vol": q.get("vol"),
                "ltp": q.get("ltp"),
                "chng": q.get("chng"),
                "chngPer": q.get("chngPer"),
                "ltt": q.get("ltt")
            }
            # Save new day's OHLC
            cache = {"date": datetime.now().strftime("%Y-%m-%d"), "ohlc": current_ohlc}
            with open(CACHE_FILE, "w") as f:
                json.dump(cache, f)
            logging.info("Saved new SENSEX OHLC")

            os.system('cls' if os.name == 'nt' else 'clear')
            table = [
                ["LTP", current_ohlc["ltp"]],
                ["Open (Day's Open)", current_ohlc["open"]],
                ["High", current_ohlc["high"]],
                ["Low", current_ohlc["low"]],
                ["Close", current_ohlc["close"]],
                ["Change", current_ohlc["chng"]],
                ["Change %", current_ohlc["chngPer"]],
                ["Volume", current_ohlc["vol"]],
                ["LTT", current_ohlc["ltt"]]
            ]
            print("SENSEX BSE Spot (-1_BSE) Live OHLC")
            print(tabulate(table, tablefmt="grid", floatfmt=".2f"))

    events.subscribe(EVENT_TICK, on_tick)

    streamer.start()
    streamer.subscribe_l1(["-1_BSE"])

    print("Subscribed to SENSEX spot — waiting for data")
    if cached_ohlc:
        print("Market closed — using last trading day OHLC:")
        table = [
            ["LTP", cached_ohlc["ltp"]],
            ["Open (Last Trading Day)", cached_ohlc["open"]],
            ["High", cached_ohlc["high"]],
            ["Low", cached_ohlc["low"]],
            ["Close", cached_ohlc["close"]],
            ["Change", cached_ohlc["chng"]],
            ["Change %", cached_ohlc["chngPer"]],
            ["Volume", cached_ohlc["vol"]],
            ["LTT", cached_ohlc["ltt"]]
        ]
        print(tabulate(table, tablefmt="grid", floatfmt=".2f"))

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        streamer.stop()
        session.close()