import csv
import io
import json
import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta
import sqlite3

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
historical_file = 'historical_symbols.json'  # For backfill symbols

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
        self.sensex_expiries = []  # Filled from BSEOptions master in workflow
        # MOD: Load watchlist moved to workflow (after expiry compute)

        # === CLEANED: Multi-timeframe candle aggregation for SENSEX spot only ===
                # === PER-SYMBOL candle aggregation ===
        self.timeframes = ["1min", "5min"]  # Add more later
        self.candles = defaultdict(dict)          # symbol -> tf -> pd.DataFrame
        self.current_candle = defaultdict(dict)   # symbol -> tf -> current dict or None
        self.load_historical_candles()
                # After logging "SENSEX Spot Token..."
        logging.info(f"SENSEX Spot Token (from Tradejini Index master): {self.sensex_spot_token}")

        self.load_historical_candles()  # ADD HERE (after token set)

    def _load_watchlist(self):
        if os.path.exists(watchlist_file):
            with open(watchlist_file, 'r') as f:
                loaded = json.load(f)
            # Deduplicate by token
            seen = set()
            self.watchlist = []
            for item in loaded:
                if item['token'] not in seen:
                    seen.add(item['token'])
                    self.watchlist.append(item)
            logging.info(f"Loaded {len(self.watchlist)} UNIQUE items from watchlist.json")

            # Set selected_symbols for tick table display (options + spot once)
            self.selected_symbols = [f"{item['token']}_BFO" for item in self.watchlist]
            if self.sensex_spot_token:
                spot_sym = f"{self.sensex_spot_token}_BSE"
                self.selected_symbols.append(spot_sym)  # Add spot only once

            # ALWAYS subscribe existing watchlist (options + spot handled inside method)
            self._subscribe_watchlist_options()
        else:
            self.watchlist = []
            self.selected_symbols = []  # Clear if no file
            logging.info("No watchlist.json found — starting empty")

    def _save_watchlist(self):
        with open(watchlist_file, 'w') as f:
            json.dump(self.watchlist, f, indent=4)
        logging.info(f"Saved watchlist to {watchlist_file}")

        # Force immediate subscription for real ticks/quotes
        option_symbols = [f"{item['token']}_BFO" for item in self.watchlist]
        if option_symbols:
            self.streamer.subscribe_l1(option_symbols)
            #if hasattr(self.streamer, 'subscribeL1SnapShot'):
            #    self.streamer.subscribeL1SnapShot(option_symbols)
            logging.info(f"IMMEDIATE subscription L1 + Snapshot for options: {option_symbols}")
       
    def start(self):
        logging.info("MarketData starting — SENSEX options workflow (as in sensex_day_open_strikes.py)")
        self.events.subscribe(EVENT_TICK, self._on_tick)
        self.events.subscribe(EVENT_CONNECT, self._on_connect)
        self._load_watchlist()  # Ensures subscription immediately
        self._sensex_options_workflow()
        #self.populate_historical_ce_pe(strikes_around_atm=5)  # ±5 strikes = 11 per day
        #self.populate_historical_ce_pe(months_back=2)
        self.populate_historical_ce_pe(days_back=30)  # or 90, 120, etc.
        # === NEW: Load historical candles after workflow (spot_token now set) ===
        if self.sensex_spot_token:
            logging.info(f"SENSEX Spot Token (from Tradejini Index master): {self.sensex_spot_token}")
            self.load_historical_candles()  # Load historical on start
        else:
            logging.warning("Spot token not set — skipping historical load")

    def stop(self):
        self._save_watchlist()  # Save on stop
        logging.info("MarketData stopping")
        self.events.unsubscribe(EVENT_TICK, self._on_tick)

    def _on_connect(self, *args):
        logging.info("Streamer connected — subscribing to SENSEX spot for open capture")

    def _on_tick(self, tick):
        symbol = tick.get('symbol')
        if not symbol:
            return

        self.quotes[symbol].update(tick)

        # Capture spot open (your existing logic — unchanged)
        spot_symbol = f"{self.sensex_spot_token}_BSE" if self.sensex_spot_token else None
        if symbol == spot_symbol and self.spot_open is None and 'open' in tick and tick['open'] > 0:
            self.spot_open = tick['open']
            with open(cache_file, 'w') as f:
                f.write(str(self.spot_open))
            logging.info(f"Captured SENSEX open from tick: {self.spot_open}")

        # Display table for watchlist options (your existing logic — adjust if selected_symbols differs)
        if symbol in self.selected_symbols:
            self._display_watchlist_tick_table()

        # === NEW: Aggregate candles for ANY symbol (spot or options) ===
        for tf in self.timeframes:
            self._aggregate_candle(symbol, tick, tf)

    def _aggregate_candle(self, symbol: str, tick: dict, tf: str):
        # Lazy initialization per symbol/tf
        if symbol not in self.candles:
            self.candles[symbol] = {}
            self.current_candle[symbol] = {}
        if tf not in self.candles[symbol]:
            df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
            df.index.name = "timestamp"
            self.candles[symbol][tf] = df
            self.current_candle[symbol][tf] = None

        # Timestamp handling (your existing logic — unchanged)
        ltt = tick.get("ltt")
        if ltt is not None:
            try:
                ltt_int = int(ltt)
                ts = datetime.fromtimestamp(ltt_int)
            except (ValueError, TypeError):
                ts = datetime.now()
        else:
            ts = datetime.now()
        ts = ts.replace(second=0, microsecond=0)
        minutes = int(tf.rstrip("min"))
        if minutes > 1:
            ts = ts.replace(minute=(ts.minute // minutes) * minutes)

        price = float(tick.get("ltp") or tick.get("close") or 0)
        volume = int(tick.get("vol") or tick.get("volume") or 0)

        if price == 0:
            logging.warning(f"Price fallback to 0 in {tf} candle for {symbol} — check tick fields")

        current = self.current_candle[symbol][tf]
        if current is None or current["ts"] != ts:
            # Close previous candle
            if current is not None:
                prev = current
                new_row = pd.DataFrame([{
                    "open": prev["open"],
                    "high": prev["high"],
                    "low": prev["low"],
                    "close": prev["close"],
                    "volume": prev["volume"]
                }], index=[prev["ts"]])
                # Avoid pandas concat warning on empty
                if self.candles[symbol][tf].empty:
                    self.candles[symbol][tf] = new_row
                else:
                    self.candles[symbol][tf] = pd.concat([self.candles[symbol][tf], new_row])

            # Start new candle
            self.current_candle[symbol][tf] = {
                "ts": ts,
                "open": price if price > 0 else 0.01,
                "high": price if price > 0 else 0.01,
                "low": price if price > 0 else 0.01,
                "close": price,
                "volume": volume
            }
        else:
            # Update current
            curr = current
            if price > 0:
                curr["high"] = max(curr["high"], price)
                curr["low"] = min(curr["low"], price)
                curr["close"] = price
            curr["volume"] += volume  # Keep your cumulative/delta logic

    def get_candles(self, symbol: str, tf: str) -> pd.DataFrame:
        """Return full candle DataFrame for a symbol + timeframe (including current incomplete)."""
        if symbol not in self.candles or tf not in self.candles[symbol]:
            return pd.DataFrame()

        df = self.candles[symbol][tf].copy()

        current = self.current_candle[symbol].get(tf)
        if current:
            curr_row = pd.DataFrame([{
                "open": current["open"],
                "high": current["high"],
                "low": current["low"],
                "close": current["close"],
                "volume": current["volume"]
            }], index=[current["ts"]])
            if df.empty:
                df = curr_row
            else:
                df = pd.concat([df, curr_row])

        df.sort_index(inplace=True)
        return df

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
        #print("\n=== Updated Watchlist Tick Data ===")
        #print(tabulate(extended_table, headers=headers, tablefmt="grid"))

        # Option A2: move to debug level (invisible unless you set logging level to DEBUG)
        logging.debug("\n=== Updated Watchlist Tick Data ===")
        logging.debug(tabulate(extended_table, headers=headers, tablefmt="grid"))

    def _sensex_options_workflow(self):
        selected_tokens = []  # Default empty list
        symbol_to_token = {}  # If used later
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
        #self.streamer.Snapshot([f"{self.sensex_spot_token}_BSE"])
        #self.streamer.subscribe_l1([f"{self.sensex_spot_token}_BSE"])

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
        symbol_map = {}      # token: symbol

        # NEW: Initialize set for unique expiry dates
        expiries_set = set()

        # Debug counters
        sensex_rows_found = 0
        expiry_parsed_count = 0

        with open(options_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Log headers once
            logging.info(f"BSEOptions CSV headers: {reader.fieldnames}")
            
            for row in reader:
                # Optional: log first few rows for debug
                if sensex_rows_found < 3:
                    logging.debug(f"Sample row: {row}")
                
                # Check for Sensex (case-insensitive)
                if 'SENSEX' in row.get('dispName', '').upper() or 'SENSEX' in row.get('id', '').upper():
                    sensex_rows_found += 1
                    
                    token = row['excToken']
                    symbol = row.get('id', '') or row.get('dispName', '')
                    strike_str = row.get('strike', None)
                    opt_type = row.get('optType', None)
                    full_id = row.get('id', '')  # This is where expiry is embedded
                    
                    # === NEW: Parse expiry from 'id' field ===
                    expiry_date = None
                    if full_id and '_' in full_id:
                        parts = full_id.split('_')
                        if len(parts) >= 4:
                            date_part = parts[3]  # YYYY-MM-DD
                            try:
                                expiry_date = datetime.strptime(date_part, '%Y-%m-%d').date()
                                expiries_set.add(expiry_date)
                                expiry_parsed_count += 1
                            except ValueError:
                                logging.debug(f"Failed to parse expiry from id: {full_id}")
                                continue
                    
                    # Your original logic (updated to use parsed expiry_date)
                    strike = None
                    if strike_str:
                        try:
                            strike = int(strike_str)
                        except:
                            pass
                    
                    if expiry_date and strike and opt_type:
                        sensex_options[(expiry_date, strike, opt_type)] = token
                    
                    symbol_map[token] = symbol
                    self.token_to_scrip[token] = f"{strike}{opt_type}" if strike else 'SENSEX'

            # After loop: store sorted expiries
            self.sensex_expiries = sorted(list(expiries_set))
            logging.info(f"Extracted {len(self.sensex_expiries)} unique Sensex expiry dates from BSEOptions master (parsed from 'id')")
            if self.sensex_expiries:
                logging.info(f"Earliest: {self.sensex_expiries[0]} | Latest: {self.sensex_expiries[-1]}")
            else:
                logging.warning("No Sensex expiries parsed — check BSEOptions CSV format")

        # NEW: Choose target expiry (earliest or user input)
        if self.sensex_expiries:
            target_expiry = self.sensex_expiries[0]  # Default earliest (weekly)
            logging.info(f"Using earliest expiry: {target_expiry}")
        else:
            target_expiry = (datetime.now() + timedelta(days=7)).date()  # Fallback next week
            logging.warning(f"No expiries — using fallback: {target_expiry}")

        # Condition 1: Add ATM ±5 strikes if not in watchlist
        existing_symbols = {item['symbol'] for item in self.watchlist}
        selected_tokens = [item['token'] for item in self.watchlist]  # Start with existing

        for offset in range(-500, 600, 100):  # ±5 strikes (11 total including ATM)
            strike = rounded_base + offset
            for opt_type in ['CE', 'PE']:
                token = sensex_options.get((target_expiry, strike, opt_type))
                symbol = symbol_map.get(token, f"SENSEX_{target_expiry}_{strike}_{opt_type}")
                
                if symbol and token and symbol not in existing_symbols:
                    self.watchlist.append({'strike': strike, 'type': opt_type, 'token': token, 'symbol': symbol, 'expiry': target_expiry})  # MOD: Add expiry
                    selected_tokens.append(token)
                    symbol_to_token[symbol] = token
                    self.token_to_scrip[token] = f"{strike}{opt_type}"

        if len(selected_tokens) > len([item['token'] for item in self.watchlist]):
            selected_tokens = list(set(selected_tokens))  # Dedupe
            logging.info(f"\nAdded ATM ±5 strikes to watchlist:")
            watchlist_table = [[item['strike'], item['type'], item['token'], item['symbol']] for item in self.watchlist]
            print(tabulate(watchlist_table, headers=["Strike", "Type", "Token", "Symbol"], tablefmt="grid"))
            logging.info(tabulate(watchlist_table, headers=["Strike", "Type", "Token", "Symbol"], tablefmt="plain"))
            self._save_watchlist()

            self.streamer.subscribe_l1([f"{t}_BFO" for t in selected_tokens] + [f"{self.sensex_spot_token}_BSE"])
            #self.streamer.Snapshot(selected_tokens + [self.sensex_spot_token])
            self.streamer.subscribe_l1(selected_tokens + [self.sensex_spot_token])

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
            if not selected_tokens:  # <<<< ADD THIS
                selected_tokens = [item['token'] for item in self.watchlist]
                logging.info(f"Falling back to {len(selected_tokens)} existing watchlist tokens")
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

    def _subscribe_watchlist_options(self):
        if not self.watchlist:
            return
        option_symbols = [f"{item['token']}_BFO" for item in self.watchlist]
        spot_symbol = f"{self.sensex_spot_token}_BSE" if self.sensex_spot_token else None
        all_symbols = set(option_symbols)  # Dedup
        if spot_symbol:
            all_symbols.add(spot_symbol)
        all_symbols = list(all_symbols)
        
        if all_symbols and hasattr(self.streamer, 'subscribe_l1'):
            self.streamer.subscribe_l1(all_symbols)
            # Fixed typo + fallback
            #if hasattr(self.streamer, 'subscribeL1SnapShot'):
            #   self.streamer.subscribeL1SnapShot(all_symbols)
            #elif hasattr(self.streamer, 'subscribeL1Snapshot'):
            #    self.streamer.subscribeL1Snapshot(all_symbols)
            logging.info(f"SUBSCRIBED L1 + Snapshot for {len(all_symbols)} symbols (spot + options)")

    def load_historical_symbols(self):
        historical_file = 'historical_symbols.json'
        
        if not os.path.exists(historical_file):
            logging.info(f"{historical_file} not found — auto-creating with default Sensex spot")
            
            # Default: Sensex spot (adjust ID if needed from symbols_Index.csv)
            default_symbols = [
                {
                    "symbol": "SENSEX_SPOT",
                    "id": "-51_BSE",  # Likely correct; check symbols_Index.csv for 'id' or 'excToken'
                    "type": "spot",
                    "description": "BSE Sensex Index (auto-added)"
                }
            ]
            
            with open(historical_file, 'w') as f:
                json.dump(default_symbols, f, indent=4)
            
            logging.info(f"Created {historical_file} with default entry")
            return default_symbols
        
        else:
            with open(historical_file, 'r') as f:
                loaded = json.load(f)
            logging.info(f"Loaded {len(loaded)} symbols for historical backfill")
            return loaded

    def load_historical_candles(self):
        # Silence detailed logging inside this method (only keep start and final summary)
        original_level = logging.getLogger().level
        logging.getLogger().setLevel(logging.WARNING)  # Suppress INFO/DEBUG during fetch

        ist = timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        market_start = now - timedelta(days=200)
        market_start = market_start.replace(hour=9, minute=15, second=0, microsecond=0)
        from_time = int(market_start.timestamp())
        to_time = int(now.timestamp())
        
        logging.info(f"Backfilling historical 1min candles for ~6 months")  # Keep this visible
        logging.debug(f"From: {market_start} ({from_time})")
        logging.debug(f"To:   {now} ({to_time})")
        
        historical_items = self.load_historical_symbols()
        if not historical_items:
            logging.debug("No historical symbols to process")
            logging.getLogger().setLevel(original_level)  # Restore
            return
        
        # NEW: Merge unique watchlist items (use 'id' or construct if missing)
        watchlist_items = self.watchlist  # From _load_watchlist (called earlier)
        all_items = historical_items.copy()  # Start with historical
        seen_ids = {item['id'] for item in all_items if 'id' in item}
        
        for wl_item in watchlist_items:
            wl_id = wl_item.get('id')
            if not wl_id:
                # Construct if missing (from symbol or other fields)
                expiry_str = wl_item.get('expiry', 'UNKNOWN')
                strike = wl_item.get('strike', '')
                opt_type = wl_item.get('type', '')
                wl_id = f"OPTIDX_SENSEX_BFO_{expiry_str}_{strike}_{opt_type}"
                wl_item['id'] = wl_id  # Add to dict for consistency
            
            if wl_id not in seen_ids:
                all_items.append(wl_item)
                seen_ids.add(wl_id)
        
        total_symbols = len(all_items)
        successful_symbols = 0
        no_data_symbols = 0
        total_bars = 0
        
        for item in all_items:
            symbol = item['symbol']
            full_id = item.get('id')
            if not full_id:
                logging.debug(f"No 'id' for {symbol} — skipping")
                continue
            
            logging.debug(f"Pulling historical 1min for {symbol} ({full_id})")
            
            db_path = 'mono_engine_data.db'
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historical_1min (
                    symbol TEXT,
                    timestamp DATETIME,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL,
                    oi REAL DEFAULT 0,
                    PRIMARY KEY (symbol, timestamp)
                )
            ''')
            conn.commit()
            
            current_from = from_time
            symbol_bars = 0
            
            while current_from < to_time:
                current_to = min(current_from + (30 * 24 * 3600), to_time)
                
                params = {
                    'id': full_id,
                    'interval': '1',
                    'from': current_from,
                    'to': current_to
                }
                
                try:
                    response = self.session.rest.get("/api/mkt-data/chart/interval-data", params=params)
                    status = response.get('s', 'unknown')
                    logging.debug(f"Chunk response: {status}")
                    
                    if status == 'ok' and 'd' in response and 'bars' in response['d']:
                        bars = response['d']['bars']
                        bars_count = len(bars)
                        logging.debug(f"Loaded {bars_count} bars in chunk")
                        
                        if bars:
                            data = []
                            for bar in bars:
                                ts_ms = bar[0]
                                ts = datetime.fromtimestamp(ts_ms / 1000, tz=ist)
                                oi = bar[6] if len(bar) > 6 else 0
                                data.append((symbol, ts, bar[1], bar[2], bar[3], bar[4], bar[5], oi))
                            
                            cursor.executemany('''
                                INSERT OR IGNORE INTO historical_1min
                                (symbol, timestamp, open, high, low, close, volume, oi)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', data)
                            conn.commit()
                            
                            df_chunk = pd.DataFrame(data, columns=['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'oi'])
                            df_chunk.set_index('timestamp', inplace=True)
                            df_chunk.drop(columns=['symbol'], inplace=True)
                            df_chunk = df_chunk.astype(float, errors='ignore')
                            
                            if '1min' not in self.candles[symbol]:
                                self.candles[symbol]['1min'] = df_chunk
                            else:
                                self.candles[symbol]['1min'] = pd.concat([self.candles[symbol]['1min'], df_chunk]).sort_index()
                            
                            logging.debug(f"Chunk saved to DB + memory ({bars_count} bars)")
                            symbol_bars += bars_count
                            total_bars += bars_count
                    
                    else:
                        logging.debug(f"No data: {response.get('msg', response)}")
                
                except Exception as e:
                    logging.error(f"Chunk failed for {symbol}: {str(e)}")
                
                current_from = current_to + 1
            
            conn.close()
            logging.debug(f"Completed historical for {symbol} (DB connection closed)")
            
            if symbol_bars > 0:
                successful_symbols += 1
            else:
                no_data_symbols += 1
        
        # Restore logging level BEFORE summary
        logging.getLogger().setLevel(original_level)
        
        # Final summary (this stays visible)
        logging.info("-" * 60)
        logging.info("Historical Backfill Summary:")
        logging.info(f"Total symbols processed: {total_symbols}")
        logging.info(f"Symbols with data fetched: {successful_symbols}")
        logging.info(f"Symbols with no data: {no_data_symbols}")
        logging.info(f"Total 1-min bars loaded: {total_bars}")
        logging.info("-" * 60)
        logging.info("All historical backfill done")
    
    def populate_historical_ce_pe(self, days_back=60):  # Start with 60 days (~2 months)
        """
        Manually construct ATM CE/PE IDs for each trading day in the last N days.
        - Uses Thursday weekly expiry assumption (next Thursday after day)
        - Exact ATM only (no buffer)
        - No dependency on symbol master CSV or self.sensex_expiries
        """
        # Silence detailed logging inside this method (only keep added count visible)
        original_level = logging.getLogger().level
        logging.getLogger().setLevel(logging.WARNING)  # Suppress INFO/DEBUG during population

        logging.debug(f"Populating manual ATM CE/PE for last {days_back} days (Thursday expiry assumption)")
        
        db_path = 'mono_engine_data.db'
        conn = sqlite3.connect(db_path)
        
        df_daily = pd.read_sql(f"""
            SELECT 
                DATE(timestamp) as trading_date,
                FIRST_VALUE(open) OVER (PARTITION BY DATE(timestamp) ORDER BY timestamp) as daily_open
            FROM historical_1min 
            WHERE symbol = 'SENSEX_SPOT'
            AND timestamp >= date('now', '-{days_back} days')
            GROUP BY trading_date
            ORDER BY trading_date DESC
        """, conn)
        
        conn.close()
        
        if df_daily.empty:
            logging.debug("No recent daily opens found — skipping")
            logging.getLogger().setLevel(original_level)  # Restore
            return
        
        logging.debug(f"Found {len(df_daily)} trading days in last {days_back} days")
        
        historical_file = 'historical_symbols.json'
        current_symbols = []
        current_ids = set()
        if os.path.exists(historical_file):
            with open(historical_file, 'r') as f:
                current_symbols = json.load(f)
            current_ids = {item['id'] for item in current_symbols}
        
        added = 0
        
        for _, row in df_daily.iterrows():
            day_str = row['trading_date']
            day = datetime.strptime(day_str, '%Y-%m-%d').date()
            open_price = row['daily_open']
            
            # Manual: next Thursday expiry
            days_to_thu = (3 - day.weekday() + 7) % 7
            if days_to_thu == 0:
                days_to_thu = 7  # if day is Thursday, take next week
            expiry_date = day + timedelta(days=days_to_thu)
            expiry_str = expiry_date.strftime('%Y-%m-%d')
            
            # Exact ATM
            atm = round(open_price / 100) * 100
            
            for opt_type in ['CE', 'PE']:
                option_id = f"OPTIDX_SENSEX_BFO_{expiry_str}_{atm}_{opt_type}"
                
                if option_id not in current_ids:
                    new_entry = {
                        "symbol": f"SENSEX {expiry_date.strftime('%d%b%y')} {atm} {opt_type}",
                        "id": option_id,
                        "type": opt_type,
                        "expiry": expiry_str,
                        "strike": atm,
                        "description": f"ATM for {day_str} open {open_price:.1f}"
                    }
                    current_symbols.append(new_entry)
                    current_ids.add(option_id)
                    added += 1
        
        if added > 0:
            with open(historical_file, 'w') as f:
                json.dump(current_symbols, f, indent=4)
            logging.info(f"Added {added} new manual ATM CE/PE entries to {historical_file}")  # Only visible log
        else:
            logging.info("No new entries needed — all already present")  # Only visible log
        
        # Restore logging level BEFORE final log
        logging.getLogger().setLevel(original_level)
        
        logging.info("Manual ATM CE/PE population complete")  # Keep this visible too