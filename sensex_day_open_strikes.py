import csv
import io
import os
from datetime import datetime

from openapi_client import Configuration, ApiClient
from openapi_client.api import SymbolDetailsApi

# Files & Cache
options_file = 'symbols_BSEOptions.csv'
index_file = 'symbols_Index.csv'
cache_file = 'last_sensex_open.txt'  # Saves last trading day's open from streamer

# Broker API setup (public for symbol master)
config = Configuration()
api_client = ApiClient(config)
api_client.default_headers['Accept'] = 'text/plain'
symbol_api = SymbolDetailsApi(api_client)

# Fetch Index group if missing (public, gets SENSEX spot token -51)
if not os.path.exists(index_file):
    print("Fetching Index group from Tradejini for SENSEX spot token...")
    raw_index = symbol_api.get_symbol_details("Index")
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(raw_index)
    print(f"Saved {index_file}")

# Extract SENSEX spot token
sensex_spot_token = None
with open(index_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'SENSEX' in row.get('dispName', '') or '-51' in str(row.get('excToken', '')) or '-51' in row.get('id', ''):
            sensex_spot_token = row['excToken']
            print(f"SENSEX Spot Token (from Tradejini Index master): {sensex_spot_token}")
            break

if not sensex_spot_token:
    print("SENSEX spot token not found — check symbols_Index.csv manually")
    exit()

# Day Open: Cache from last trading day (streamer captures on live days)
if os.path.exists(cache_file):
    with open(cache_file, 'r') as f:
        day_open = float(f.read().strip())
    print(f"Loaded last trading day's open from broker cache: {day_open}")
else:
    day_open = 83540.43  # Initial fallback (updates on first trading day run)
    print(f"No cache yet — using fallback {day_open} (real open captured on trading day via streamer)")

# Grid settings
strike_interval = 100
num_offsets = 10  # +10 CE / -10 PE

base_strike = round(day_open / strike_interval) * strike_interval
ce_strikes = [base_strike + (i * strike_interval) for i in range(1, num_offsets + 1)]
pe_strikes = [base_strike - (i * strike_interval) for i in range(1, num_offsets + 1)]
target_strikes = sorted(pe_strikes + ce_strikes)

print(f"\nDay Open: {day_open} → Rounded Base: {base_strike}")
print(f"CE (+{num_offsets}): {ce_strikes}")
print(f"PE (-{num_offsets}): {pe_strikes}\n")

# Load SENSEX options from saved BSEOptions (broker data)
sensex_options = {}
with open(options_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'SENSEX' in row['id']:
            parts = row['id'].split('_')
            if len(parts) >= 6:
                expiry = parts[3]
                strike = int(parts[4])
                opt_type = parts[5]
                sensex_options[(expiry, strike, opt_type)] = row['excToken']

# Nearest weekly expiry (Thursday/Wednesday shift, 'w' flagged near-term)
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
    print(f"Selected Weekly Expiry (from Tradejini data): {target_expiry} ({nearest_weekly[0].strftime('%d %b %Y %A')})\n")
else:
    target_expiry = expiries[-1]
    print(f"Fallback Expiry: {target_expiry}\n")

# Table + Tokens (includes spot token for open capture)
print("| Strike | CE Token     | PE Token     | Offset |")
print("|--------|--------------|--------------|--------|")

selected_tokens = [sensex_spot_token]  # Spot for open + live LTP
for strike in target_strikes:
    ce_token = sensex_options.get((target_expiry, strike, 'CE'))
    pe_token = sensex_options.get((target_expiry, strike, 'PE'))
    offset = strike - base_strike
    offset_str = f"+{offset}" if offset > 0 else str(offset)
    print(f"| {strike:<6} | {ce_token or 'N/A':<12} | {pe_token or 'N/A':<12} | {offset_str}   |")
    if ce_token: selected_tokens.append(ce_token)
    if pe_token: selected_tokens.append(pe_token)

print(f"\nTotal Tokens: {len(selected_tokens)} (spot + 40 options — subscribe in nxtradstream)")
print("Tokens:", selected_tokens)

print("\nFully Broker-Auto (Tradejini):")
print("- Symbol master (Index + BSEOptions): Direct from Tradejini public API.")
print("- Open price: Cached from broker streamer packet (captured on trading days).")
print("- On Sunday/weekend: Uses last trading day's open (Feb 6, 2026).")
print("- On trading day: Run streamer early → auto-captures/saves today's open from SENSEX packet.")

print("\nStreamer Capture Code (add to nxtradstream packet handler):")
print("if token == sensex_spot_token and packet_type == 'L1' and 'open' in packet:")
print("    today_open = packet['open']")
print("    with open('last_sensex_open.txt', 'w') as f:")
print("        f.write(str(today_open))")
print("    print(f'Captured today\\'s SENSEX open: {today_open} → saved for grid')")

print("\nRun on trading morning → real open auto-saved. Next runs use it.")