import csv
import io
import json

from openapi_client.api.symbol_details_api import SymbolDetailsApi
from openapi_client.api_client import ApiClient
from openapi_client.configuration import Configuration

config = Configuration()
api_client = ApiClient(configuration=config)
symbol_api = SymbolDetailsApi(api_client)

# FORCE CSV FORMAT (critical — many APIs default to JSON without this)
symbol_api.api_client.default_headers['Accept'] = 'text/plain'  # or try 'text/csv'

print("Fetching version_details(0)...\n")

response = symbol_api.version_details(0)

if response.s != 'ok':
    print("Error:", response)
    exit()

data = response.d
print(f"Version: {data.version}")
print(f"Updated: {data.updated}")

print("\nAvailable Scrip Groups:")
groups = [item.name for item in data.symbol_store]
for name in groups:
    print(f" - {name}")

# Test groups
test_groups = ["Securities", "BSEOptions", "NSEOptions"]

for target_group in test_groups:
    if target_group not in groups:
        continue
    
    print(f"\nFetching symbols for: {target_group} ...")
    
    raw_data = symbol_api.get_symbol_details(target_group)
    
    print(f"Raw response length: {len(raw_data)} characters")
    
    # ALWAYS SAVE RAW for manual check
    raw_filename = f"raw_{target_group}.txt"
    with open(raw_filename, 'w', encoding='utf-8') as f:
        f.write(raw_data)
    print(f"  Saved raw → {raw_filename}")
    
    # DEBUG: First 20 lines
    print("  First 20 lines of raw response:")
    lines = raw_data.splitlines()
    for line in lines[:20]:
        print("   ", line)
    print("  ... (end preview)\n")
    
    # TRY CSV PARSE
    parsed = False
    try:
        reader = csv.DictReader(io.StringIO(raw_data))
        symbols = list(reader)
        
        if symbols:
            print(f"  CSV Success! Parsed {len(symbols)} symbols")
            print("  Columns:", list(symbols[0].keys()))
            print("  Sample row:", symbols[0])
            
            csv_filename = f"symbols_{target_group}.csv"
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                f.write(raw_data)
            print(f"  Saved parsed CSV → {csv_filename}")
            
            if target_group == "BSEOptions":
                sensex_symbols = [r for r in symbols if 'SENSEX' in r.get('symbol', '') or 'SENSEX' in r.get('trading_symbol', '') or 'SENSEX' in r.get('name', '')]
                print(f"  SENSEX-related: {len(sensex_symbols)}")
                if sensex_symbols:
                    print("  Sample SENSEX:", sensex_symbols[0])
            parsed = True
        else:
            print("  CSV parsed but 0 rows (headers only?)")
    except Exception as e:
        print("  CSV parse failed:", e)
    
    # FALLBACK: Try JSON if CSV failed or 0 rows
    if not parsed or not symbols if 'symbols' in locals() else True:
        try:
            symbols_json = json.loads(raw_data)
            print(f"  JSON Success! Parsed {len(symbols_json)} symbols (list/dict)")
            print("  Sample:", symbols_json[0] if isinstance(symbols_json, list) else symbols_json)
            
            json_filename = f"symbols_{target_group}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(symbols_json, f, indent=2)
            print(f"  Saved JSON → {json_filename}")
        except Exception as json_e:
            print("  JSON parse also failed:", json_e)

print("\nDone — check raw_*.txt, CSVs, or JSON files.")