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
        self._load_watchlist()  # Load persistent watchlist

    def _load_watchlist(self):
        if os.path.exists(watchlist_file):
            with open(watchlist_file, 'r') as f:
                self.watchlist = json.load(f)
            logging.info(f"Loaded {len(self.watchlist)} items from watchlist.json")

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
    def get_scrip_details(self, symbol):
        """Fetch token/lot for symbol from Tradejini API/cache."""
        try:
            resp = self.engine.session.rest.get("/api/master/symbols")  # Adapt to Tradejini endpoint for symbol master
            # Parse for symbol (mock for test)
            return {'token': '12345', 'lot_size': 50}  # Real: parse resp for symbol
        except:
            return {'token': 'mock_token', 'lot_size': 50}
        
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

        if not self.sensex_spot_token:
            logging.error("SENSEX spot token not found — check symbols_Index.csv manually")
            return

        # Subscribe to spot for open capture
        spot_symbol = f"{self.sensex_spot_token}_BSE"  # Adapt to project symbol format
        self.streamer.subscribe_l1([spot_symbol])

        # NEW: Check if it's potentially market hours (IST, Mon-Fri, ~9AM-4PM) to decide if waiting makes sense
        now_ist = datetime.now(timezone('Asia/Kolkata'))
        is_weekday = now_ist.weekday() < 5  # 0-4 = Mon-Fri
        is_market_time = now_ist.hour >= 9 and now_ist.hour < 16  # Rough window
        wait_duration = 60 if is_weekday and is_market_time else 10  # Shorter wait on off-days

        # Day Open: Try streamer first, then cache, then fallback
        logging.info(f"Waiting up to {wait_duration}s for SENSEX spot open from streamer...")
        start_time = time.time()
        while self.spot_open is None and time.time() - start_time < wait_duration:
            # NEW: Actively check quotes for 'open' field during wait
            if spot_symbol in self.quotes and 'open' in self.quotes[spot_symbol] and self.quotes[spot_symbol]['open'] > 0:
                self.spot_open = self.quotes[spot_symbol]['open']
                with open(cache_file, 'w') as f:
                    f.write(str(self.spot_open))
                logging.info(f"Captured SENSEX open from streamer quotes: {self.spot_open}")
            time.sleep(1)

        if self.spot_open is None:
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    self.spot_open = float(f.read().strip())
                logging.info(f"Loaded last trading day's open from cache: {self.spot_open}")
            else:
                self.spot_open = 83540.43  # Script fallback
                logging.info(f"No cache/streamer data — using fallback {self.spot_open}")

        # Grid settings (exact as script)
        strike_interval = 100
        num_offsets = 10

        base_strike = round(self.spot_open / strike_interval) * strike_interval
        ce_strikes = [base_strike + (i * strike_interval) for i in range(1, num_offsets + 1)]
        pe_strikes = [base_strike - (i * strike_interval) for i in range(1, num_offsets + 1)]
        target_strikes = sorted(pe_strikes + ce_strikes)

        logging.info(f"\nDay Open: {self.spot_open} → Rounded Base: {base_strike}")
        logging.info(f"CE (+{num_offsets}): {ce_strikes}")
        logging.info(f"PE (-{num_offsets}): {pe_strikes}\n")

        # Fetch BSEOptions if missing
        if not os.path.exists(options_file):
            logging.info("Fetching BSEOptions from Tradejini...")
            raw_options = symbol_api.get_symbol_details("BSEOptions")
            with open(options_file, 'w', encoding='utf-8') as f:
                f.write(raw_options)
            logging.info(f"Saved {options_file}")

        # Load SENSEX options from CSV (exact as script) + build symbol map
        sensex_options = {}
        symbol_map = {}  # For full symbols
        with open(options_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'SENSEX' in row['id']:
                    parts = row['id'].split('_')
                    if len(parts) >= 6:
                        expiry = parts[3]
                        strike = int(parts[4])
                        opt_type = parts[5]
                        token = row['excToken']
                        sensex_options[(expiry, strike, opt_type)] = token
                        symbol_map[token] = row['id']  # Full symbol like SENSEX_2026-02-12_83000_CE

        # Nearest weekly expiry (exact as script)
        today = datetime.now()
        expiries = sorted(set(k[0] for k in sensex_options.keys()))
        weekly_expiries = []
        for exp_str in expiries:
            try:
                exp_date = datetime.strptime(exp_str, '%Y-%m-%d')
                if exp_date.weekday() in [3, 2]:  # Thursday=3, Wednesday=2
                    weekly_expiries.append((exp_date, exp_str))
            except:
                pass

        if weekly_expiries:
            nearest_weekly = min([e for e in weekly_expiries if e[0] >= today], key=lambda x: x[0], default=weekly_expiries[0])
            target_expiry = nearest_weekly[1]
            logging.info(f"Selected Weekly Expiry (from Tradejini data): {target_expiry} ({nearest_weekly[0].strftime('%d %b %Y %A')})\n")
        else:
            target_expiry = expiries[-1] if expiries else None
            logging.info(f"Fallback Expiry: {target_expiry}\n")

        if not target_expiry:
            logging.error("No expiries found — manual input required")
            return

        # Build table data with row numbers (for selection)
        table_data = []
        row_map = {}  # Row num to (strike, type, token)
        row_num = 1
        for strike in target_strikes:
            for opt_type in ['PE', 'CE']:  # List PE then CE per strike for finer selection
                token = sensex_options.get((target_expiry, strike, opt_type))
                if token:
                    offset = strike - base_strike
                    offset_str = f"+{offset}" if offset > 0 else str(offset)
                    table_data.append([row_num, strike, opt_type, token, offset_str])
                    row_map[row_num] = (strike, opt_type, token)
                    row_num += 1

        # Display table (now with row #, type separate)
        headers = ["#", "Strike", "Type", "Token", "Offset"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))  # Console for user
        logging.info(tabulate(table_data, headers=headers, tablefmt="plain"))  # Log plain

        total_options = len(table_data)
        logging.info(f"\nTotal Options: {total_options} (PE/CE for grid) + spot")

        # Condition 1: User choice for watchlist
        user_input = input("\nEnter row numbers to add to watchlist (comma-separated/ranges, e.g., '1,3-5,7', or 'all' for everything): ").strip().lower()
        selected_rows = set()
        if user_input == 'all':
            selected_rows = set(range(1, row_num))
        else:
            parts = user_input.split(',')
            for part in parts:
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    selected_rows.update(range(start, end + 1))
                elif part.isdigit():
                    selected_rows.add(int(part))

        # Build initial watchlist and tokens from condition 1
        selected_tokens = [self.sensex_spot_token]  # Always include spot
        symbol_to_token = {}
        existing_symbols = {item['symbol'] for item in self.watchlist}  # For dedupe
        for r in selected_rows:
            if r in row_map:
                strike, opt_type, token = row_map[r]
                symbol = symbol_map.get(token, f"SENSEX_{target_expiry}_{strike}_{opt_type}")
                if symbol not in existing_symbols:
                    self.watchlist.append({'strike': strike, 'type': opt_type, 'token': token, 'symbol': symbol})
                    existing_symbols.add(symbol)
                selected_tokens.append(token)
                symbol_to_token[symbol] = token
                # NEW: Populate token_to_scrip
                self.token_to_scrip[token] = f"{strike}{opt_type}"

        # For spot
        self.token_to_scrip[self.sensex_spot_token] = "SENSEX"

        # Dedupe tokens
        selected_tokens = list(set(selected_tokens))

        logging.info(f"\nAdded/Updated {len(self.watchlist)} symbols to watchlist:")
        watchlist_table = [[item['strike'], item['type'], item['token'], item['symbol']] for item in self.watchlist]
        print(tabulate(watchlist_table, headers=["Strike", "Type", "Token", "Symbol"], tablefmt="grid"))  # Show to user
        logging.info(tabulate(watchlist_table, headers=["Strike", "Type", "Token", "Symbol"], tablefmt="plain"))
        self._save_watchlist()  # Save after condition 1

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
                        self.watchlist.append({'strike': item['strike'], 'type': 'CE', 'token': item['token'], 'symbol': item['symbol']})
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
        self.streamer.subscribe_l2(self.selected_symbols)  # Add subscribe_l2 for depth data
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