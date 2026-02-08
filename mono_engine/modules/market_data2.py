import logging
import os
import time
from collections import defaultdict

from tabulate import tabulate

from mono_engine.modules.base import BaseModule
from mono_engine.core.events import EVENT_TICK, EVENT_CONNECT

class MarketData(BaseModule):
    def __init__(self, engine):
        super().__init__(engine)
        self.quotes = defaultdict(dict)
        self.subscribed = set()
        self.spot_open = None
        self.selected_symbols = []

    def start(self):
        logging.info("MarketData starting — SENSEX options workflow")
        self.events.subscribe(EVENT_TICK, self._on_tick)
        self.events.subscribe(EVENT_CONNECT, self._on_connect)

        self._sensex_options_workflow()

    def stop(self):
        logging.info("MarketData stopping")
        self.events.unsubscribe(EVENT_TICK, self._on_tick)

    def _sensex_options_workflow(self):
        spot_symbol = "-1_BSE"
        self.streamer.subscribe_l1([spot_symbol])

        logging.info("Waiting for SENSEX spot data (includes day's open even after close)...")
        start_time = time.time()
        while self.spot_open is None and time.time() - start_time < 30:
            time.sleep(1)

        if self.spot_open is None:
            self.spot_open = float(input("No spot open received — enter SENSEX open price manually: "))

        logging.info(f"SENSEX day's open captured: {self.spot_open:.2f}")

        selected_input = input("\nEnter option tokens to monitor (comma-separated BFO tokens, e.g., 12345,67890): ").strip()
        selected_tokens = [t.strip() for t in selected_input.split(",") if t.strip()]
        selected_symbols = [f"{t}_BFO" for t in selected_tokens]
        selected_symbols.append(spot_symbol)

        self.selected_symbols = selected_symbols
        self.streamer.subscribe_l1(selected_symbols)
        self.streamer.subscribe_greeks(selected_tokens)  # Tokens only for greeks
        logging.info(f"Monitoring {len(selected_symbols)} symbols with greeks")

    def _on_connect(self, data):
        logging.info("MarketData: WS connected")

    def _on_tick(self, data):
        msg_type = data.get("msgType")
        if msg_type == "marketStatus":
            return

        symbol = data.get("symbol")
        if not symbol:
            return

        self.quotes[symbol].update(data)

        if symbol == "-1_BSE" and "open" in data and self.spot_open is None:
            self.spot_open = data["open"]

        if symbol in self.selected_symbols:
            os.system('cls' if os.name == 'nt' else 'clear')
            table_data = []
            for sym in self.selected_symbols:
                q = self.quotes[sym]
                bid_depth = " | ".join([f"{p.get('price',0):.2f}@{p.get('qty',0)}" for p in q.get("bid", [])[:5]])
                ask_depth = " | ".join([f"{p.get('price',0):.2f}@{p.get('qty',0)}" for p in q.get("ask", [])[:5]])
                row = {
                    "Symbol": sym,
                    "LTP": q.get("ltp", 0),
                    "Open": q.get("open", 0),
                    "High": q.get("high", 0),
                    "Low": q.get("low", 0),
                    "Close": q.get("close", 0),
                    "Chg": q.get("chng", 0),
                    "Chg%": q.get("chngPer", 0),
                    "Vol": q.get("vol", 0),
                    "OI": q.get("OI", 0),
                    "Prev OI": q.get("prevOI", 0),
                    "Day High OI": q.get("dayHighOI", 0),
                    "Day Low OI": q.get("dayLowOI", 0),
                    "ATP": q.get("atp", 0),
                    "VWAP": q.get("vwap", 0),
                    "LTT": q.get("ltt", ""),
                    "Delta": q.get("delta", 0),
                    "Gamma": q.get("gamma", 0),
                    "Vega": q.get("vega", 0),
                    "Theta": q.get("theta", 0),
                    "Rho": q.get("rho", 0),
                    "IV": q.get("iv", 0),
                    "High IV": q.get("highiv", 0),
                    "Low IV": q.get("lowiv", 0),
                    "ITM": q.get("itm", 0),
                    "Depth": f"B: {bid_depth} || A: {ask_depth}"
                }
                table_data.append(row)

            print(f"SENSEX Day Open: {self.spot_open:.2f if self.spot_open else 'Waiting...'}")
            print(tabulate(table_data, headers="keys", tablefmt="grid", floatfmt=".2f"))