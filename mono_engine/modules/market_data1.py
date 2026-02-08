import logging
import os
import sqlite3
import time
from datetime import datetime, timedelta
from collections import defaultdict

import pandas as pd
from tabulate import tabulate

from mono_engine.modules.base import BaseModule
from mono_engine.core.events import EVENT_TICK, EVENT_CONNECT

DB_PATH = "mono_engine_data.db"

class MarketData(BaseModule):
    """
    Full SENSEX options workflow with live tabular display, greeks, DB cache.
    Shows day's open for SENSEX even after market close.
    """

    def __init__(self, engine):
        super().__init__(engine)
        self.quotes = defaultdict(dict)
        self.subscribed = set()
        self.options_df = pd.DataFrame()
        self.spot_open = None
        self.selected_symbols = []

    def start(self):
        logging.info("MarketData starting — SENSEX options workflow")
        self.events.subscribe(EVENT_TICK, self._on_tick)
        self.events.subscribe(EVENT_CONNECT, self._on_connect)

        self._init_db()
        self._load_or_fetch_bfo_options()

        self._sensex_options_workflow()

    def stop(self):
        logging.info("MarketData stopping")
        self.events.unsubscribe(EVENT_TICK, self._on_tick)

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""CREATE TABLE IF NOT EXISTS bfo_options (
            exc_token TEXT PRIMARY KEY, tradingsymbol TEXT, underlying TEXT, expiry TEXT, strike REAL, option_type TEXT,
            lot_size INTEGER, tick_size REAL, OI INTEGER
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS ticks (
            timestamp TEXT, symbol TEXT, data TEXT
        )""")
        conn.close()

    def _load_or_fetch_bfo_options(self):
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM bfo_options", conn)
        conn.close()
        if not df.empty and len(df) > 100:
            self.options_df = df
            logging.info(f"Loaded {len(df)} BFO options from DB cache")
        else:
            logging.info("Fetching BFO options from broker...")
            try:
                resp = self.session.rest.get("/api/mkt-data/scrips/symbol-store/BFO")
                logging.info(f"Raw BFO response keys: {list(resp.keys()) if isinstance(resp, dict) else 'list response'}")
                data = resp.get("d", resp) if isinstance(resp, dict) else resp
                if not data:
                    logging.error("Empty BFO data")
                    return
                df = pd.DataFrame(data)
                logging.info(f"BFO columns: {list(df.columns)} | Rows: {len(df)}")
                # Mapping from Tradejini response
                column_map = {
                    "excToken": "exc_token",
                    "strikePrice": "strike",
                    "optionType": "option_type",
                    "expiryDate": "expiry",
                    "underlying": "underlying",
                }
                df = df.rename(columns=column_map)
                df['strike'] = pd.to_numeric(df.get("strike", df.get("strikePrice", 0)), errors='coerce')
                df['OI'] = pd.to_numeric(df.get("OI", df.get("openInterest", 0)), errors='coerce')
                df.to_sql("bfo_options", sqlite3.connect(DB_PATH), if_exists="replace", index=False)
                self.options_df = df
                logging.info(f"Fetched and cached {len(df)} BFO options")
            except Exception as e:
                logging.error(f"BFO fetch failed: {e}")

    def _get_current_weekly_expiry(self):
        today = datetime.now().date()
        days_to_thursday = (3 - today.weekday()) % 7
        thursday = today + timedelta(days=days_to_thursday)
        if days_to_thursday == 0:
            return thursday.strftime("%d-%m-%Y")
        return thursday.strftime("%d-%m-%Y")

    def _sensex_options_workflow(self):
        expiry = self._get_current_weekly_expiry()
        logging.info(f"Detected weekly expiry: {expiry}")

        underlying_col = "underlying" if "underlying" in self.options_df.columns else "name"
        option_type_col = "option_type" if "option_type" in self.options_df.columns else "optionType"
        expiry_col = "expiry" if "expiry" in self.options_df.columns else "expiryDate"
        strike_col = "strike" if "strike" in self.options_df.columns else "strikePrice"
        token_col = "exc_token" if "exc_token" in self.options_df.columns else "token"

        options = self.options_df[
            (self.options_df[underlying_col] == "SENSEX") &
            (self.options_df[expiry_col] == expiry)
        ]
        if options.empty:
            logging.warning(f"No options for {expiry} — fallback to manual")
            expiry = input("Enter expiry (dd-mm-yyyy): ").strip()
            options = self.options_df[
                (self.options_df[underlying_col] == "SENSEX") &
                (self.options_df[expiry_col] == expiry)
            ]

        if options.empty:
            logging.error("No SENSEX options — manual token input")
            manual_tokens = input("Enter option tokens (comma-separated): ").strip()
            selected_tokens = [t.strip() for t in manual_tokens.split(",") if t.strip()]
            selected_symbols = [f"{t}_BFO" for t in selected_tokens]
            self.selected_symbols = selected_symbols + ["-1_BSE"]
            self.subscribe(self.selected_symbols, greeks=True)
            return

        spot_symbol = "-1_BSE"
        self.subscribe([spot_symbol])

        logging.info("Waiting for SENSEX spot data...")
        start_time = time.time()
        while self.spot_open is None and time.time() - start_time < 30:
            time.sleep(1)

        if self.spot_open is None:
            self.spot_open = float(input("Enter SENSEX open price manually: "))

        atm_strike = round(self.spot_open / 100) * 100
        logging.info(f"SENSEX day's open: {self.spot_open:.2f} | ATM: {atm_strike}")

        ce = options[(options[option_type_col] == "CE") & (options[strike_col] >= atm_strike)].sort_values("OI", ascending=False).head(10)
        pe = options[(options[option_type_col] == "PE") & (options[strike_col] <= atm_strike)].sort_values("OI", ascending=False).head(10)

        print("\nRecommended CE (highest OI):")
        print(tabulate(ce[[strike_col, 'OI', token_col]], headers=["Strike", "OI", "Token"], tablefmt="grid"))
        print("\nRecommended PE (highest OI):")
        print(tabulate(pe[[strike_col, 'OI', token_col]], headers=["Strike", "OI", "Token"], tablefmt="grid"))

        selected_input = input("\nEnter tokens to monitor (comma-separated, or Enter for top 5 CE + PE): ").strip()
        if not selected_input:
            selected_tokens = ce.head(5)[token_col].tolist() + pe.head(5)[token_col].tolist()
        else:
            selected_tokens = [t.strip() for t in selected_input.split(",") if t.strip()]

        selected_symbols = [f"{t}_BFO" for t in selected_tokens]
        selected_symbols.append(spot_symbol)

        self.selected_symbols = selected_symbols
        self.subscribe(selected_symbols, greeks=True)
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

        # DB log
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO ticks VALUES (?, ?, ?)", (datetime.now().isoformat(), symbol, str(data)))
        conn.commit()
        conn.close()

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
                    "Delta": q.get("delta", 0),
                    "Gamma": q.get("gamma", 0),
                    "Vega": q.get("vega", 0),
                    "Theta": q.get("theta", 0),
                    "Rho": q.get("rho", 0),
                    "IV": q.get("iv", 0),
                    "ITM": q.get("itm", 0),
                    "Depth": f"B: {bid_depth} || A: {ask_depth}"
                }
                table_data.append(row)

            print(f"SENSEX Day Open: {self.spot_open:.2f if self.spot_open else 'Waiting...'}")
            print(tabulate(table_data, headers="keys", tablefmt="grid", floatfmt=".2f"))

    def subscribe(self, symbols, greeks=False):
        new_symbols = [s for s in symbols if s not in self.subscribed]
        if new_symbols:
            self.streamer.subscribe_l1(new_symbols)
            if greeks:
                tokens = [s.split("_")[0] for s in new_symbols if "_BFO" in s]
                if tokens:
                    self.streamer.nx_stream.subscribeGreeks(tokens)
            self.subscribed.update(new_symbols)
            logging.info(f"Subscribed to {len(new_symbols)} symbols (greeks={greeks})")