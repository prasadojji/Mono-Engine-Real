import csv
import io
import os
from datetime import datetime

from openapi_client.api.symbol_details_api import SymbolDetailsApi
from openapi_client.api_client import ApiClient
from openapi_client.configuration import Configuration

class SymbolStore:
    def __init__(self, cache_file='symbol_cache.json'):
        self.cache_file = cache_file
        self.version = None
        self.groups = []
        self.symbols_by_token = {}  # Main dict: excToken -> full row dict
        self.symbols_by_group = {}  # group -> list of rows
        self.load_from_cache()      # Try load persisted

    def fetch_and_update(self, force=False):
        config = Configuration()
        api_client = ApiClient(configuration=config)
        # Force CSV
        api_client.default_headers['Accept'] = 'text/plain'
        symbol_api = SymbolDetailsApi(api_client)

        # Check version
        response = symbol_api.version_details(0 if force else self.version or 0)
        if response.s != 'ok':
            raise ValueError("Version check failed")

        data = response.d
        updated = data.updated
        new_version = data.version

        if not force and not updated and self.version == new_version:
            print("Symbol store up-to-date (version", new_version, ")")
            return False

        print(f"Updating symbol store → version {new_version} (updated: {updated})")
        self.version = new_version
        self.groups = [item.name for item in data.symbol_store]
        self.symbols_by_token.clear()
        self.symbols_by_group.clear()

        # Fetch desired groups (add/remove as needed)
        target_groups = ["Securities", "NSEOptions", "BSEOptions", "FutureContracts", "Index"]

        for group in target_groups:
            if group not in self.groups:
                print(f"Skipping {group} (not available)")
                continue
            print(f"Fetching {group}...")
            raw_csv = symbol_api.get_symbol_details(group)
            if not raw_csv.strip():
                continue

            reader = csv.DictReader(io.StringIO(raw_csv))
            rows = list(reader)
            self.symbols_by_group[group] = rows

            for row in rows:
                token = row.get('excToken')
                if token:
                    self.symbols_by_token[token] = row

            print(f"  Loaded {len(rows)} symbols")

        self.save_to_cache()
        return True

    def get_by_token(self, token):
        return self.symbols_by_token.get(str(token))

    def find_atm_options(self, underlying_name="BANKEX", target_date=None):
        """Find ATM strikes for options (closest to current LTP - but LTP not here yet)"""
        options = [r for r in self.symbols_by_group.get("BSEOptions", []) if underlying_name.upper() in r['dispName'].upper()]
        if not options:
            print(f"No options found for {underlying_name}")
            return []

        # Group by expiry
        expiries = {}
        for r in options:
            # Parse from id: e.g., OPTIDX_BANKEX_BFO_2026-02-26_56100_CE
            parts = r['id'].split('_')
            if len(parts) >= 7:
                expiry = parts[4]
                strike = parts[5]
                opt_type = parts[6]
                expiries.setdefault(expiry, []).append({
                    'strike': float(strike),
                    'type': opt_type,
                    'token': r['excToken'],
                    'row': r
                })

        # Example: Print nearest expiry ATM (need LTP for real ATM)
        print(f"Found {len(options)} {underlying_name} options across expiries")
        for exp, strikes in expiries.items():
            strikes.sort(key=lambda x: x['strike'])
            mid = len(strikes) // 2
            atm = strikes[mid]
            print(f"  {exp} ATM approx: {atm['strike']} {atm['type']} (token {atm['token']})")

        return options

    def save_to_cache(self):
        import json
        cache_data = {
            'version': self.version,
            'timestamp': datetime.now().isoformat(),
            'symbols_by_token': self.symbols_by_token
        }
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f)
        print(f"Cache saved → {self.cache_file}")

    def load_from_cache(self):
        if not os.path.exists(self.cache_file):
            return
        import json
        with open(self.cache_file) as f:
            data = json.load(f)
        self.version = data.get('version')
        self.symbols_by_token = data.get('symbols_by_token', {})
        print(f"Loaded cache (version {self.version}, {len(self.symbols_by_token)} tokens)")

# Test usage
if __name__ == "__main__":
    store = SymbolStore()
    store.fetch_and_update(force=False)  # Set force=True for fresh download
    # Example: Find BANKEX ATM approx
    store.find_atm_options("BANKEX")
    # For SENSEX if appears later
    # store.find_atm_options("SENSEX")