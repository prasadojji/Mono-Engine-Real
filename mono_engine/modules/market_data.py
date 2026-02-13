import csv
import io
import json
import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta

import pandas as pd
from openapi_client import Configuration, ApiClient
from openapi_client.api import SymbolDetailsApi
from tabulate import tabulate

from mono_engine.modules.base import BaseModule
from mono_engine.core.events import EVENT_TICK, EVENT_CONNECT

# NEW: For IST time checks
from pytz import timezone  # Add this import; if not installed, use manual UTC+5:30 offset

# Files & Cache (relative to project root or config path)
options_file = 'symbols_BSEOptions.csv'
index_file = 'symbols_Index.csv'
cache_file = 'last_sensex_open.txt'
watchlist_file = 'watchlist.json'  # New for persistence

class MarketData(BaseModule):
    def __init__(self, engine):
        super().__init__(engine)
        self.quotes = defaultdict(dict)
        self.subscribed = set()
        self.spot_open = None
        self.selected_symbols = []
        self.sensex_spot_token = None
        self.watchlist = []  # List of dicts {'strike': int, 'type': str, 'token': str, 'symbol': str}
        self.token_to_scrip = {}  # NEW: Map token to user-friendly scrip name
        # MOD: Load watchlist moved to workflow (after expiry compute)

    def _load_watchlist(self):
        if os.path.exists(watchlist_file):
            with open(watchlist_file, 'r') as f:
                self.watchlist = json.load(f)
            logging.info(f"Loaded {len(self.watchlist)} items from watchlist.json")
        else:
            self.watchlist = []

    def _save_watchlist(self):
        with open(watchlist_file, 'w') as f:
            json.dump(self.watchlist, f, indent=4)
        logging.info(f"Saved watchlist to {watchlist_file}")

    def start(self):
        logging.info("MarketData starting — SENSEX options workflow (as in sensex_day_open_strikes.py)")
        self.events.subscribe(EVENT_TICK, self._on_tick)
        self.events.subscribe(EVENT_CONNECT, self._on_connect)

        self._sensex_options_workflow()

    def stop(self):
        self._save_watchlist()  # Save on stop
        logging.info("MarketData stopping")
        self.events.unsubscribe(EVENT_TICK, self._on_tick)

    def _on_connect(self, *args):
        logging.info("Streamer connected — subscribing to SENSEX spot for open capture")

    def _on_tick(self, tick):
        symbol = tick.get('symbol')
        if symbol:
            self.quotes[symbol].update(tick)
            # Capture spot open as soon as a valid tick arrives (safeguard if loop misses it)
            spot_symbol = f"{self.sensex_spot_token}_BSE"
            if symbol == spot_symbol and self.spot_open is None and 'open' in tick and tick['open'] > 0:
                self.spot_open = tick['open']
                with open(cache_file, 'w') as f:
                    f.write(str(self.spot_open))
                logging.info(f"Captured SENSEX open from tick: {self.spot_open}")

            # NEW: If symbol is in selected_symbols (watchlist), display updated table
            if symbol in self.selected_symbols:
                self._display_watchlist_tick_table()

    def _display_watchlist_tick_table(self):
        extended_table = []
        for item in self.watchlist + [{'strike': None, 'type': 'SPOT', 'token': self.sensex_spot_token, 'symbol': 'SENSEX_SPOT'}]:  # Include spot
            token = item['token']
            quote = self.quotes.get(f"{token}_BSE" if item['strike'] is None else f"{token}_BFO", {})
            
            # User-friendly scrip name
            scrip = "SENSEX" if item['strike'] is None else f"{item['strike']}{item['type']}"

            # Extract key data from tick/quote
            ltt = quote.get('ltt', 'N/A')  # Last trade time
            ltp = quote.get('ltp', 'N/A')
            chng = quote.get('chng', 'N/A')
            chngPer = quote.get('chngPer', 'N/A')
            open_val = quote.get('open', 'N/A')
            high = quote.get('high', 'N/A')
            low = quote.get('low', 'N/A')
            close = quote.get('close', 'N/A')
            vol = quote.get('vol', 'N/A')
            oi = quote.get('OI', 'N/A')
            bidPrice = quote.get('bidPrice', 'N/A')
            askPrice = quote.get('askPrice', 'N/A')
            qty = quote.get('qty', 'N/A')  # Assuming qty is for bid/ask
            totBuyQty = quote.get('totBuyQty', 'N/A')
            totSellQty = quote.get('totSellQty', 'N/A')

            row = [
                scrip,
                ltt,
                ltp,
                chng,
                chngPer,
                f"{open_val}/{high}/{low}/{close}",
                vol,
                oi,
                f"{bidPrice}x{qty}",
                f"{askPrice}x{qty}",
                f"Bids: {totBuyQty} | Asks: {totSellQty}"
            ]
            extended_table.append(row)

        headers = [
            "Scrip", "Last Time", "LTP", "Change", "% Change", "OHLC",
            "Volume", "OI", "Best Bid", "Best Ask", "Depth"
        ]
        print("\n=== Updated Watchlist Tick Data ===")
        print(tabulate(extended_table, headers=headers, tablefmt="grid"))

    def _sensex_options_workflow(self):
        # Broker API setup (public for symbol master)
        config = Configuration()
        api_client = ApiClient(config)
        api_client.default_headers['Accept'] = 'text/plain'
        symbol_api = SymbolDetailsApi(api_client)

        # Fetch Index group if missing (gets SENSEX spot token -51)
        if not os.path.exists(index_file):
            logging.info("Fetching Index group from Tradejini for SENSEX spot token...")
            raw_index = symbol_api.get_symbol_details("Index")
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(raw_index)
            logging.info(f"Saved {index_file}")

        # Extract SENSEX spot token
        with open(index_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'SENSEX' in row.get('dispName', '') or '-51' in str(row.get('excToken', '')) or '-51' in row.get('id', ''):
                    self.sensex_spot_token = row['excToken']
                    logging.info(f"SENSEX Spot Token (from Tradejini Index master): {self.sensex_spot_token}")
                    break

        # Subscribe to SENSEX spot for open price
        self.streamer.subscribe_l1([f"{self.sensex_spot_token}_BSE"])
        self.streamer.snapshot([f"{self.sensex_spot_token}_BSE"])

        # Wait for spot open from streamer (or fallback to cache)
        logging.info("Waiting up to 10s for SENSEX spot open from streamer...")
        start_time = time.time()
        while self.spot_open is None and time.time() - start_time < 10:
            time.sleep(1)
        if self.spot_open is None and os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                self.spot_open = float(f.read().strip())
            logging.info(f"Used cached SENSEX open: {self.spot_open}")
        elif self.spot_open is None:
            self.spot_open = 84200.0  # Manual fallback if no data (adjust)
            logging.warning(f"No spot open data. Using fallback: {self.spot_open}")

        # Compute rounded base and grid strikes
        rounded_base = round(self.spot_open / 100) * 100
        logging.info(f"Day Open: {self.spot_open} → Rounded Base: {rounded_base}")

        target_strikes = [rounded_base + offset for offset in range(-1000, 1100, 100)]  # ±10 strikes

        logging.info(f"CE (+10): {target_strikes[10:]}")
        logging.info(f"PE (-10): {target_strikes[:10][::-1]}")  # Reverse for descending

        # Fetch BSEOptions group if missing
        if not os.path.exists(options_file):
            logging.info("Fetching BSEOptions group from Tradejini...")
            raw_options = symbol_api.get_symbol_details("BSEOptions")
            with open(options_file, 'w', encoding='utf-8') as f:
                f.write(raw_options)
            logging.info(f"Saved {options_file}")

        # Parse BSEOptions CSV for tokens/symbols
        sensex_options = {}  # (expiry, strike, type): token
        symbol_map = {}  # token: symbol
        with open(options_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'SENSEX' in row.get('dispName', '') or 'SENSEX' in row.get('id', ''):
                    token = row['excToken']
                    symbol = row.get('id', '') or row.get('dispName', '')  # Full symbol
                    strike = row.get('strike', None)
                    opt_type = row.get('optType', None)
                    expiry_str = row.get('expiry', None)
                    if expiry_str and strike and opt_type:
                        expiry = datetime.strptime(expiry_str, '%d%b%y').date()  # DDMMMYY to date
                        sensex_options[(expiry, int(strike), opt_type) ] = token
                    symbol_map[token] = symbol
                    self.token_to_scrip[token] = f"{strike}{opt_type}" if strike else 'SENSEX'  # User-friendly

        # Compute target expiry (weekly, Thursday)
        today = datetime.now(timezone('Asia/Kolkata')).date()  # IST
        days_to_thursday = (3 - today.weekday() + 7) % 7  # Wednesday is 2, Thursday 3
        target_expiry = today + timedelta(days=days_to_thursday or 7)  # Next Thursday if today Thursday

        logging.info(f"Selected Weekly Expiry (from Tradejini data): {target_expiry} ({target_expiry.strftime('%d %b %Y')} Thursday)")

        # Load watchlist and existing
        self._load_watchlist()
        existing_symbols = [item['symbol'] for item in self.watchlist]
        existing_tokens = [item['token'] for item in self.watchlist]

        # Condition 1: Prompt to add from grid (only new)
        grid_table = []
        row_num = 1
        for offset in range(-1000, 1100, 100):
            strike = rounded_base + offset
            for opt_type in ['PE', 'CE']:
                token = sensex_options.get((target_expiry, strike, opt_type))
                symbol = symbol_map.get(token, f"OPTIDX_SENSEX_BFO_{target_expiry.strftime('%Y-%m-%d')}_{strike}_{opt_type}")
                if token and symbol not in existing_symbols:
                    grid_table.append([row_num, strike, opt_type, token, offset])
                    row_num += 1

        if not grid_table:
            logging.info("No new grid options available — all already in watchlist or no data")
        else:
            print("\nAvailable Grid Options (new only):")
            print(tabulate(grid_table, headers=["#", "Strike", "Type", "Token", "Offset"], tablefmt="grid"))
            logging.info(tabulate(grid_table, headers=["#", "Strike", "Type", "Token", "Offset"], tablefmt="plain"))

            user_input = input("\nEnter row numbers to add to watchlist (comma-separated/ranges, e.g., '1,3-5,7', or 'all' for everything): ").strip().lower()
            if user_input == 'all':
                add_rows = range(1, len(grid_table) + 1)
            elif user_input:
                add_rows = []
                for part in user_input.split(','):
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        add_rows.extend(range(start, end + 1))
                    else:
                        add_rows.append(int(part))
            else:
                add_rows = []

            selected_tokens = existing_tokens.copy()
            for r in add_rows:
                if 1 <= r <= len(grid_table):
                    strike, opt_type, token, offset = grid_table[r-1][1:]
                    symbol = symbol_map.get(token, f"OPTIDX_SENSEX_BFO_{target_expiry.strftime('%Y-%m-%d')}_{strike}_{opt_type}")
                    self.watchlist.append({'strike': strike, 'type': opt_type, 'token': token, 'symbol': symbol})
                    selected_tokens.append(token)
                    self.token_to_scrip[token] = f"{strike}{opt_type}"

            if add_rows:
                print("\nAdded/Updated symbols to watchlist:")
                watchlist_table = [[item['strike'], item['type'], item['token'], item['symbol']] for item in self.watchlist]
                print(tabulate(watchlist_table, headers=["Strike", "Type", "Token", "Symbol"], tablefmt="grid"))
                logging.info(tabulate(watchlist_table, headers=["Strike", "Type", "Token", "Symbol"], tablefmt="plain"))
                self._save_watchlist()

            self.streamer.subscribe_l1([f"{t}_BFO" for t in selected_tokens] + [f"{self.sensex_spot_token}_BSE"])
            self.streamer.snapshot(selected_tokens + [self.sensex_spot_token])

        # Condition 2: Propose top scrips with high upside potential
        # First, subscribe to ALL grid options temporarily for data (volume, greeks)
        all_tokens = []
        for strike in target_strikes:
            for opt_type in ['PE', 'CE']:
                token = sensex_options.get((target_expiry, strike, opt_type))
                if token:
                    all_tokens.append(token)
        all_symbols = [f"{t}_BFO" for t in all_tokens] + [f"{self.sensex_spot_token}_BSE"]
        self.streamer.subscribe_l1(all_symbols)
        self.streamer.subscribe_greeks(all_tokens)  # Greeks for options

        # Wait for data (up to 20s for more coverage)
        logging.info("Waiting up to 20s for grid market data to analyze proposals...")
        start_time = time.time()
        while time.time() - start_time < 20:
            time.sleep(1)

        # Analyze: Build DF for CE only (bullish focus)
        analysis_data = []
        for strike in target_strikes:
            token = sensex_options.get((target_expiry, strike, 'CE'))
            if token:
                sym = f"{token}_BFO"
                quote = self.quotes.get(sym, {})
                volume = quote.get('volume', 0)  # Default 0 if N/A
                delta = quote.get('delta', 0)
                iv = quote.get('iv', float('inf'))  # High if N/A
                oi = quote.get('oi', 0)  # If available in quote
                analysis_data.append({
                    'strike': strike,
                    'token': token,
                    'volume': volume,
                    'delta': delta,
                    'iv': iv,
                    'oi': oi,
                    'symbol': symbol_map.get(token, f"SENSEX_{target_expiry}_{strike}_CE")
                })

        if not analysis_data:
            logging.info("No data available for proposals (market closed?) — skipping condition 2")
        else:
            df = pd.DataFrame(analysis_data)
            # Filter/sort for high upside: delta >0.4, iv <25, sort by volume desc (or OI if volume 0)
            sort_key = 'volume' if df['volume'].sum() > 0 else 'oi'
            potential_df = df[(df['delta'] > 0.4) & (df['iv'] < 25)].sort_values(sort_key, ascending=False).head(5)  # Top 5 candidates, pick 2 not in watchlist

            proposals = []
            for _, row in potential_df.iterrows():
                if row['symbol'] not in existing_symbols and len(proposals) < 2:  # At least 2 new
                    proposals.append(row.to_dict())

            if not proposals:
                logging.info("No new high-potential scrips found — all top ones already in watchlist or no data")
            else:
                # Display proposals
                prop_table = [[i+1, row['strike'], 'CE', row['token'], row['volume'], row['delta'], row['iv']] for i, row in enumerate(proposals)]
                headers = ["#", "Strike", "Type", "Token", "Volume", "Delta", "IV"]
                print("\nProposed High-Upside Scrips (top volume + bullish greeks):")
                print(tabulate(prop_table, headers=headers, tablefmt="grid"))
                logging.info(tabulate(prop_table, headers=headers, tablefmt="plain"))

                # Prompt to add
                prop_input = input("\nAdd proposed to watchlist? (y for all, comma-separated #s, or Enter to skip): ").strip().lower()
                if prop_input == 'y':
                    add_rows = range(1, len(proposals) + 1)
                elif prop_input:
                    add_rows = [int(p) for p in prop_input.split(',') if p.isdigit()]
                else:
                    add_rows = []

                for r in add_rows:
                    if 1 <= r <= len(proposals):
                        item = proposals[r-1]
                        self.watchlist.append({'strike': item['strike'], 'type': 'CE', 'token': item['token'], 'symbol': item['symbol'], 'expiry': target_expiry})  # MOD: Add expiry
                        selected_tokens.append(item['token'])
                        symbol_to_token[item['symbol']] = item['token']
                        self.token_to_scrip[item['token']] = f"{item['strike']}CE"  # Update map for new additions

                if add_rows:
                    selected_tokens = list(set(selected_tokens))  # Dedupe
                    logging.info(f"\nUpdated watchlist with {len(add_rows)} proposals:")
                    watchlist_table = [[item['strike'], item['type'], item['token'], item['symbol']] for item in self.watchlist]
                    print(tabulate(watchlist_table, headers=["Strike", "Type", "Token", "Symbol"], tablefmt="grid"))
                    logging.info(tabulate(watchlist_table, headers=["Strike", "Type", "Token", "Symbol"], tablefmt="plain"))
                    self._save_watchlist()

        # Final subscriptions (only selected + spot)
        self.selected_symbols = [f"{t}_BFO" if t != self.sensex_spot_token else f"{t}_BSE" for t in selected_tokens]
        self.streamer.subscribe_l1(self.selected_symbols)
        #self.streamer.subscribe_l2(self.selected_symbols)  # Add subscribe_l2 for depth data
        option_tokens = [t for t in selected_tokens if t != self.sensex_spot_token]
        if option_tokens:
            self.streamer.subscribe_greeks(option_tokens)
        logging.info(f"Monitoring {len(self.selected_symbols)} symbols with greeks")

        

        # Additional script notes in logs
        logging.info("\nFully Broker-Auto (Tradejini):")
        logging.info("- Symbol master (Index + BSEOptions): Direct from Tradejini public API.")
        logging.info("- Open price: Cached from broker streamer packet (captured on trading days).")
        logging.info("- On Sunday/weekend: Uses last trading day's open.")
        logging.info("- On trading day: Streamer auto-captures/saves today's open from SENSEX packet.")