import csv
import io
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

# Files & Cache (relative to project root or config path)
options_file = 'symbols_BSEOptions.csv'
index_file = 'symbols_Index.csv'
cache_file = 'last_sensex_open.txt'

class MarketData(BaseModule):
    def __init__(self, engine):
        super().__init__(engine)
        self.quotes = defaultdict(dict)
        self.subscribed = set()
        self.spot_open = None
        self.selected_symbols = []
        self.sensex_spot_token = None
        self.watchlist = []  # List of dicts {'strike': int, 'type': str, 'token': str, 'symbol': str}

    def start(self):
        logging.info("MarketData starting — SENSEX options workflow (as in sensex_day_open_strikes.py)")
        self.events.subscribe(EVENT_TICK, self._on_tick)
        self.events.subscribe(EVENT_CONNECT, self._on_connect)

        self._sensex_options_workflow()

    def stop(self):
        logging.info("MarketData stopping")
        self.events.unsubscribe(EVENT_TICK, self._on_tick)

    def _on_connect(self, *args):
        logging.info("Streamer connected — subscribing to SENSEX spot for open capture")

    def _on_tick(self, tick):
        symbol = tick.get('symbol')
        if symbol:
            # Update quotes with all available data
            self.quotes[symbol].update(tick)
            # Optionally log or print updates, but avoid spam

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

        # Day Open: Try streamer first, then cache, then fallback
        logging.info("Waiting up to 60s for SENSEX spot open from streamer...")
        start_time = time.time()
        while self.spot_open is None and time.time() - start_time < 60:
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

        # User choice for watchlist (enhanced prompt)
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

        # Build watchlist and tokens
        selected_tokens = [self.sensex_spot_token]  # Always include spot
        symbol_to_token = {}  # For lookup
        for r in selected_rows:
            if r in row_map:
                strike, opt_type, token = row_map[r]
                symbol = symbol_map.get(token, f"SENSEX_{target_expiry}_{strike}_{opt_type}")
                self.watchlist.append({'strike': strike, 'type': opt_type, 'token': token, 'symbol': symbol})
                selected_tokens.append(token)
                symbol_to_token[symbol] = token

        # Dedupe tokens
        selected_tokens = list(set(selected_tokens))

        logging.info(f"\nAdded {len(self.watchlist)} symbols to watchlist:")
        watchlist_table = [[item['strike'], item['type'], item['token'], item['symbol']] for item in self.watchlist]
        print(tabulate(watchlist_table, headers=["Strike", "Type", "Token", "Symbol"], tablefmt="grid"))  # Show to user
        logging.info(tabulate(watchlist_table, headers=["Strike", "Type", "Token", "Symbol"], tablefmt="plain"))

        # Adapt to project symbols and subscribe (as before, plus depth for bid/ask levels)
        self.selected_symbols = [f"{t}_BFO" if t != self.sensex_spot_token else f"{t}_BSE" for t in selected_tokens]
        self.streamer.subscribe_l1(self.selected_symbols)
        #self.streamer.subscribe_depth(self.selected_symbols)  # Add for full depth (assume method exists) - OJJI
        option_tokens = [t for t in selected_tokens if t != self.sensex_spot_token]
        if option_tokens:
            self.streamer.subscribe_greeks(option_tokens)
        logging.info(f"Monitoring {len(self.selected_symbols)} symbols with greeks and depth")

        # Wait for initial data (up to 10s)
        logging.info("Waiting up to 10s for initial market data...")
        start_time = time.time()
        while time.time() - start_time < 10:
            if all(sym in self.quotes and 'ltp' in self.quotes[sym] for sym in self.selected_symbols):
                break
            time.sleep(1)

        # Display extended watchlist data
        self._display_watchlist_data(target_expiry, symbol_to_token)

        # Additional script notes in logs
        logging.info("\nFully Broker-Auto (Tradejini):")
        logging.info("- Symbol master (Index + BSEOptions): Direct from Tradejini public API.")
        logging.info("- Open price: Cached from broker streamer packet (captured on trading days).")
        logging.info("- On Sunday/weekend: Uses last trading day's open.")
        logging.info("- On trading day: Streamer auto-captures/saves today's open from SENSEX packet.")

    def _display_watchlist_data(self, expiry, symbol_to_token):
        extended_table = []
        for item in self.watchlist + [{'strike': None, 'type': 'SPOT', 'token': self.sensex_spot_token, 'symbol': 'SENSEX_SPOT'}]:  # Include spot
            sym = item['symbol']
            token = item['token']
            quote = self.quotes.get(f"{token}_BSE" if 'SPOT' in sym else f"{token}_BFO", {})
            
            # Extract data (assume tick keys: ltp, open, high, low, close, volume, bid_price, bid_qty, ask_price, ask_qty, delta, gamma, theta, vega, iv, depth as list of dicts, etc.)
            ltp = quote.get('ltp', 'N/A')
            o = quote.get('open', 'N/A')
            h = quote.get('high', 'N/A')
            l = quote.get('low', 'N/A')
            c = quote.get('close', 'N/A')  # Prev close or current
            vol = quote.get('volume', 'N/A')
            bid = f"{quote.get('bid_price', 'N/A')}x{quote.get('bid_qty', 'N/A')}"
            ask = f"{quote.get('ask_price', 'N/A')}x{quote.get('ask_qty', 'N/A')}"
            delta = quote.get('delta', 'N/A')
            gamma = quote.get('gamma', 'N/A')
            theta = quote.get('theta', 'N/A')
            vega = quote.get('vega', 'N/A')
            iv = quote.get('iv', 'N/A')  # Implied volatility
            # Depth: Summarize top 1-2 levels if available (assume quote['depth'] = {'bids': [(p,q),...], 'asks': [(p,q),...]})
            depth = quote.get('depth', {})
            bid_depth = '; '.join([f"{p}x{q}" for p, q in depth.get('bids', [])[:2]]) if depth else 'N/A'
            ask_depth = '; '.join([f"{p}x{q}" for p, q in depth.get('asks', [])[:2]]) if depth else 'N/A'
            depth_str = f"Bids: {bid_depth} | Asks: {ask_depth}"

            row = [
                item['strike'] or 'SPOT',
                item['type'],
                token,
                sym,
                ltp,
                f"{o}/{h}/{l}/{c}",
                vol,
                bid,
                ask,
                delta,
                gamma,
                theta,
                vega,
                iv,
                depth_str
            ]
            extended_table.append(row)

        headers = [
            "Strike", "Type", "Token", "Symbol", "LTP", "OHLC", "Volume", "Best Bid", "Best Ask",
            "Delta", "Gamma", "Theta", "Vega", "IV", "Depth (Top 2)"
        ]
        print("\nWatchlist Market Data:")
        print(tabulate(extended_table, headers=headers, tablefmt="grid"))  # Console display
        logging.info("\nWatchlist Market Data:")
        logging.info(tabulate(extended_table, headers=headers, tablefmt="plain"))