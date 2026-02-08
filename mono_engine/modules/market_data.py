import logging
import os
import requests
import time
from datetime import datetime, timedelta
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

        logging.info("Waiting up to 60s for SENSEX spot data...")
        start_time = time.time()
        while self.spot_open is None and time.time() - start_time < 60:
            time.sleep(1)

        if self.spot_open is None:
            self.spot_open = float(input("No open received — enter SENSEX open price manually: "))

        logging.info(f"SENSEX day's open: {self.spot_open:.2f}")

        # Fetch BFO (direct requests as in SDK test)
        base_url = "https://api.tradejini.com/v2"
        try:
            resp = requests.get(f"{base_url}/api/mkt-data/scrips/symbol-store/BFO")
            logging.info(f"BFO status: {resp.status_code} | Raw: {resp.text[:500]}")
            if resp.status_code == 200:
                data = resp.json() if resp.headers.get('Content-Type') == 'application/json' else []
                if isinstance(data, dict):
                    data = data.get("d", data)
                df = pd.DataFrame(data)
                logging.info(f"BFO rows: {len(df)} | Columns: {list(df.columns)}")
            else:
                df = pd.DataFrame()
        except Exception as e:
            logging.error(f"BFO fetch failed: {e}")
            df = pd.DataFrame()

        if df.empty:
            logging.warning("No BFO data — manual token input")
            selected_input = input("\nEnter BFO tokens to monitor (comma-separated): ").strip()
            selected_tokens = [t.strip() for t in selected_input.split(",") if t.strip()]
        else:
            # Robust mapping
            column_map = {
                "excToken": "exc_token",
                "strikePrice": "strike",
                "optionType": "option_type",
                "expiryDate": "expiry",
                "underlying": "underlying",
            }
            df = df.rename(columns=column_map)
            df['strike'] = pd.to_numeric(df.get("strike", df.get("strikePrice", 0)), errors='coerce')
            df['OI'] = pd.to_numeric(df.get("OI", 0), errors='coerce')

            underlying_col = "underlying" if "underlying" in df.columns else "name"
            option_type_col = "option_type" if "option_type" in df.columns else "optionType"
            expiry_col = "expiry" if "expiry" in df.columns else "expiryDate"
            strike_col = "strike" if "strike" in df.columns else "strikePrice"
            token_col = "exc_token" if "exc_token" in df.columns else "token"

            expiry = self._get_current_weekly_expiry()
            options = df[
                (df[underlying_col] == "SENSEX") &
                (df[expiry_col] == expiry)
            ]

            if options.empty:
                logging.warning("No SENSEX options for expiry — manual input")
                selected_input = input("\nEnter BFO tokens to monitor (comma-separated): ").strip()
                selected_tokens = [t.strip() for t in selected_input.split(",") if t.strip()]
            else:
                atm_strike = round(self.spot_open / 100) * 100
                ce = options[(options[option_type_col] == "CE") & (options[strike_col] >= atm_strike)].sort_values("OI", ascending=False).head(10)
                pe = options[(options[option_type_col] == "PE") & (options[strike_col] <= atm_strike)].sort_values("OI", ascending=False).head(10)

                print("\nTop 10 CE (highest OI):")
                print(tabulate(ce[[strike_col, 'OI', token_col]], headers=["Strike", "OI", "Token"], tablefmt="grid"))
                print("\nTop 10 PE (highest OI):")
                print(tabulate(pe[[strike_col, 'OI', token_col]], headers=["Strike", "OI", "Token"], tablefmt="grid"))

                selected_input = input("\nEnter tokens to monitor (comma-separated, or Enter for top 20): ").strip()
                if not selected_input:
                    selected_tokens = ce[token_col].tolist() + pe[token_col].tolist()
                else:
                    selected_tokens = [t.strip() for t in selected_input.split(",") if t.strip()]

        selected_symbols = [f"{t}_BFO" for t in selected_tokens]
        selected_symbols.append(spot_symbol)

        self.selected_symbols = selected_symbols
        self.streamer.subscribe_l1(selected_symbols)
        if selected_tokens:
            self.streamer.subscribe_greeks(selected_tokens)
        logging.info(f"Monitoring {len(selected_symbols)} symbols with greeks")

    # _on_tick, subscribe, etc. remain the same as previous full version

    # (Paste the _on_tick and subscribe from previous message)

    def _get_current_weekly_expiry(self):
        today = datetime.now().date()
        days_to_thursday = (3 - today.weekday()) % 7
        thursday = today + timedelta(days=days_to_thursday)
        if today.weekday() >= 4:  # Friday or later — next Thursday
            thursday += timedelta(days=7)
        return thursday.strftime("%d-%m-%Y")