import csv
import io
import json

from openapi_client import Configuration, ApiClient
from openapi_client.api import SymbolDetailsApi

# Critical: Use the v2 base URL per official docs
config = Configuration(host="https://api.tradejini.com/v2")

api_client = ApiClient(config)
symbol_api = SymbolDetailsApi(api_client)

print("Fetching scrip groups and version...\n")

try:
    # First-time or full check: use version=0
    version_response = symbol_api.version_details(version=0)
    
    print("Version Response:")
    print(f"  Is Updated: {version_response.is_updated}")
    print(f"  New Version: {version_response.version}")
    
    if hasattr(version_response, 'groups') and version_response.groups:
        groups = [group.name for group in version_response.groups]
        print(f"  Valid Scrip Groups ({len(groups)}): {groups}")
    else:
        print("  No groups returned — might need to check host or try again.")
except Exception as e:
    print("Error calling version_details:", e)
    print("(If host error, try without /v2: https://api.tradejini.com)")
    exit()

# Test fetch for a known group (Securities = Equity)
if 'groups' in locals() and groups:
    # Use the first group or force "Securities" if present
    test_group = "Securities" if "Securities" in groups else groups[0]
    print(f"\nFetching symbols for group: {test_group}")
    
    try:
        raw_data = symbol_api.get_symbol_details(test_group)
        
        if not raw_data or not raw_data.strip():
            print("  Empty response — no data for this group yet.")
        else:
            # Parse as CSV (default/recommended)
            try:
                reader = csv.DictReader(io.StringIO(raw_data))
                symbols = list(reader)
                print(f"  Success! Parsed {len(symbols)} symbols (CSV format)")
                print("  Columns:", list(symbols[0].keys()) if symbols else "None")
                print("  Sample symbol:", symbols[0] if symbols else "None")
                
                # Optional: Save full CSV locally
                with open(f'symbols_{test_group}.csv', 'w', newline='') as f:
                    f.write(raw_data)
                print(f"  Saved to symbols_{test_group}.csv")
            except Exception as csv_e:
                print("  CSV parse issue:", csv_e)
                # Fallback JSON
                symbols = json.loads(raw_data)
                print(f"  Parsed {len(symbols)} symbols (JSON)")
                print("  Sample:", symbols[0] if symbols else "None")
    except Exception as e:
        print("Error fetching symbols for group:", e)
else:
    # Fallback: Directly test "Securities" (known valid for equity)
    print("\nFallback: Directly testing known group 'Securities'")
    try:
        raw_data = symbol_api.get_symbol_details("Securities")
        # ... (same parsing/saving as above)
        reader = csv.DictReader(io.StringIO(raw_data))
        symbols = list(reader)
        print(f"  Parsed {len(symbols)} symbols")
        print("  Sample:", symbols[0])
        with open('symbols_Securities.csv', 'w', newline='') as f:
            f.write(raw_data)
    except Exception as e:
        print("Fallback failed:", e)