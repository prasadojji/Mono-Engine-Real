import os
import time
from datetime import datetime
import csv
import io
import logging
from tabulate import tabulate  # For readable table

import json  # For watchlist JSON

class SensexOptions:
    def __init__(self, engine):
        self.name = "sensex_options"
        self.spot_token = None
        self.options_file = 'symbols_BSEOptions.csv'
        self.index_file = 'symbols_Index.csv'
        self.cache_file = 'last_sensex_open.txt'
        self.sensex_options = {}
        self.engine = engine
        self.watchlist = []
        self.watchlist_file = 'watchlist.json'
        self.load_symbols()

    def load_symbols(self):
        # Fetch Index/BSEOptions if missing (public)
        from openapi_client import Configuration, ApiClient
        from openapi_client.api import SymbolDetailsApi

        config = Configuration()
        api_client = ApiClient(config)
        api_client.default_headers['Accept'] = 'text/plain'
        symbol_api = SymbolDetailsApi(api_client)

        if not os.path.exists(self.index_file):
            raw_index = symbol_api.get_symbol_details("Index")
            with open(self.index_file, 'w', encoding='utf-8') as f:
                f.write(raw_index)
        if not os.path.exists(self.options_file):
            raw_options = symbol_api.get_symbol_details("BSEOptions")
            with open(self.options_file, 'w', encoding='utf-8') as f:
                f.write(raw_options)

        # Spot token
        with open(self.index_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'SENSEX' in row.get('dispName', '') or '-51' in row.get('excToken', ''):
                    self.spot_token = row['excToken']
                    break

        # Load options
        with open(self.options_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'SENSEX' in row['id']:
                    parts = row['id'].split('_')
                    if len(parts) >= 6:
                        expiry_str = parts[3]  # YYYY-MM-DD
                        strike = int(parts[4])
                        opt_type = parts[5]
                        self.sensex_options[(expiry_str, strike, opt_type)] = {
                            'dispName': row['dispName'],
                            'token': row['excToken'],
                            'lot': row['lot'],
                            'weekly': row['weekly']
                        }

    def _load_watchlist(self):
        if os.path.exists(self.watchlist_file):
            with open(self.watchlist_file, 'r') as f:
                self.watchlist = json.load(f)
            logging.info(f"Loaded {len(self.watchlist)} items from watchlist.json")
        else:
            self.watchlist = []

    def _save_watchlist(self):
        with open(self.watchlist_file, 'w') as f:
            json.dump(self.watchlist, f, indent=4)
        logging.info(f"Saved watchlist with {len(self.watchlist)} items")

    def _parse_selection(self, selection, grid):
        selected = []
        if selection == 'all':
            selected = list(range(1, len(grid) + 1))
        else:
            parts = selection.split(',')
            for part in parts:
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    selected.extend(range(start, end + 1))
                else:
                    selected.append(int(part))
        return selected

    def start(self):
        logging.info("sensex_options starting — SENSEX options workflow")
        if self.spot_token is None:
            logging.error("SENSEX spot token not found — check symbols_Index.csv")
            return

        # Subscribe spot for open capture
        spot_symbol = f"{self.spot_token}_BSE"
        self.engine.streamer.subscribe_l1([spot_symbol])
        if hasattr(self.engine.streamer, 'subscribeL1SnapShot'):
            self.engine.streamer.subscribeL1SnapShot([spot_symbol])
        logging.info(f"Subscribed L1 + snapshot for spot: {spot_symbol}")

        # Get day_open (from cache or tick)
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                day_open = float(f.read().strip())
            logging.info(f"Loaded last trading day's open from cache: {day_open}")
        else:
            day_open = 83968.43  # Fallback
            logging.info(f"Using fallback day open: {day_open}")

        # Strike grid logic
        strike_interval = 100
        num_offsets = 10
        base_strike = round(day_open / strike_interval) * strike_interval
        ce_strikes = [base_strike + (i * strike_interval) for i in range(1, num_offsets + 1)]
        pe_strikes = [base_strike - (i * strike_interval) for i in range(1, num_offsets + 1)]
        target_strikes = sorted(pe_strikes + ce_strikes + [base_strike])  # + ATM

        # Nearest weekly
        today = datetime.now()
        expiries = sorted(set(k[0] for k in self.sensex_options.keys()))
        weekly_expiries = [(datetime.strptime(e, '%Y-%m-%d'), e) for e in expiries if datetime.strptime(e, '%Y-%m-%d').weekday() in [2, 3]]
        nearest_weekly = min([e for e in weekly_expiries if e[0] >= today], key=lambda x: x[0], default=weekly_expiries[0])
        target_expiry = nearest_weekly[1]
        print(f"Weekly: {target_expiry}")

        # Check if to clear watchlist (only on Friday)
        if today.weekday() == 4:  # Friday
            self.watchlist = []
            logging.info("Cleared watchlist for new week")
        else:
            self._load_watchlist()

        # Grid
        grid = []
        for i, strike in enumerate(target_strikes, 1):
            ce_key = (target_expiry, strike, 'CE')
            pe_key = (target_expiry, strike, 'PE')
            ce_disp = self.sensex_options.get(ce_key, {}).get('dispName', 'N/A')
            pe_disp = self.sensex_options.get(pe_key, {}).get('dispName', 'N/A')
            offset = strike - base_strike
            class_type = 'ATM' if offset == 0 else 'ITM' if offset < 0 else 'OTM'
            grid.append([i, strike, class_type, ce_disp, pe_disp, offset])

        # Table (readable with tabulate)
        print("\nGrid (select 1,3,5-7 or all)")
        print(tabulate(grid, headers=["#", "Strike", "Type", "CE Symbol", "PE Symbol", "Offset"], tablefmt="grid"))

        # Prompt for selection
        selection = input("\nEnter row numbers to add to watchlist (comma-separated/ranges, e.g., '1,3-5,7', or 'all' for everything): ").strip().lower()
        if selection:
            selected_rows = self._parse_selection(selection, grid)
            for row_num in selected_rows:
                if 1 <= row_num <= len(grid):
                    item = grid[row_num - 1]
                    strike = item[1]
                    # Add CE
                    ce_key = (target_expiry, strike, 'CE')
                    if ce_key in self.sensex_options:
                        ce = self.sensex_options[ce_key]
                        self.watchlist.append({'strike': strike, 'type': 'CE', 'token': ce['token'], 'symbol': ce['dispName'], 'expiry': target_expiry})
                    # Add PE
                    pe_key = (target_expiry, strike, 'PE')
                    if pe_key in self.sensex_options:
                        pe = self.sensex_options[pe_key]
                        self.watchlist.append({'strike': strike, 'type': 'PE', 'token': pe['token'], 'symbol': pe['dispName'], 'expiry': target_expiry})
            self._save_watchlist()
            logging.info(f"Added {len(selected_rows)*2} items (CE/PE) to watchlist")

        # Selection and rest (copy from earlier)

# In mono_engine/engine.py: Add to self.modules load
# self.modules.append(SensexOptions(self))