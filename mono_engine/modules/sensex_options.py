import os
import time
from datetime import datetime
import csv
import io

#from mono_engine.core import ModuleBase

#class SensexOptions(ModuleBase):
class SensexOptions:
    def __init__(self, engine):
        #super().__init__(engine)
        self.name = "sensex_options"
        self.spot_token = None
        self.options_file = 'symbols_BSEOptions.csv'
        self.index_file = 'symbols_Index.csv'
        self.cache_file = 'last_sensex_open.txt'
        self.sensex_options = {}
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
                        expiry = parts[3]
                        strike = int(parts[4])
                        opt_type = parts[5]
                        key = (expiry, strike, opt_type)
                        self.sensex_options[key] = {
                            'token': row['excToken'],
                            'dispName': row['dispName']
                        }

    def start(self):
        print(f"{self.name} starting — SENSEX options workflow")
        self.engine.streamer.subscribe([self.spot_token])  # Subscribe spot for open

        # Wait for open
        max_retries = 10
        retry_delay = 60
        for attempt in range(max_retries):
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    day_open = float(f.read().strip())
                print(f"Open: {day_open}")
                break
            if datetime.now().weekday() >= 5:
                day_open = float(input("Weekend — manual open: "))
                break
            print(f"Waiting open... ({attempt+1})")
            time.sleep(retry_delay)
        else:
            day_open = float(input("No open — manual: "))

        # Grid calculation and logic (copy from earlier code — table, selection, chosen_symbols, subscribe, live loop)
        strike_interval = 100
        num_offsets = 10
        base_strike = round(day_open / strike_interval) * strike_interval
        ce_strikes = [base_strike + (i * strike_interval) for i in range(1, num_offsets + 1)]
        pe_strikes = [base_strike - (i * strike_interval) for i in range(1, num_offsets + 1)]
        target_strikes = sorted(pe_strikes + ce_strikes + [base_strike]) # + ATM

        # Nearest weekly
        today = datetime.now()
        expiries = sorted(set(k[0] for k in self.sensex_options.keys()))
        weekly_expiries = [(datetime.strptime(e, '%Y-%m-%d'), e) for e in expiries if datetime.strptime(e, '%Y-%m-%d').weekday() in [2, 3]]
        nearest_weekly = min([e for e in weekly_expiries if e[0] >= today], key=lambda x: x[0], default=weekly_expiries[0])
        target_expiry = nearest_weekly[1]
        print(f"Weekly: {target_expiry}")

        # Grid
        grid = []
        for i, strike in enumerate(target_strikes, 1):
            ce_key = (target_expiry, strike, 'CE')
            pe_key = (target_expiry, strike, 'PE')
            ce_disp = self.sensex_options.get(ce_key, {}).get('dispName', 'N/A')
            pe_disp = self.sensex_options.get(pe_key, {}).get('dispName', 'N/A')
            offset = strike - base_strike
            class_type = 'ATM' if offset == 0 else 'ITM' if offset < 0 else 'OTM'
            grid.append((i, strike, class_type, ce_disp, pe_disp, offset))

        # Table
        print("\nGrid (select 1,3,5-7 or all)")
        print("| # | Strike | Type | CE Symbol | PE Symbol | Offset |")
        print("|---|--------|------|-----------|-----------|--------|")
        for item in grid:
            print(f"| {item[0]:<1} | {item[1]:<6} | {item[2]:<4} | {item[3]:<30} | {item[4]:<30} | {item[5]:<6} |")

        # Selection and rest (copy from earlier)

# In mono_engine/engine.py: Add to self.modules load
# self.modules.append(SensexOptions(self))