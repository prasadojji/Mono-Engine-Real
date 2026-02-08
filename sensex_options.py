import csv
from collections import defaultdict
from datetime import datetime

filename = 'symbols_BSEOptions.csv'

sensex_rows = []
expiries = set()
strikes_by_expiry = defaultdict(list)

with open(filename, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'SENSEX' in row['id'] or 'SENSEX' in row['dispName']:
            sensex_rows.append(row)
            
            # Accurate parse from id: OPTIDX_SENSEX_BFO_YYYY-MM-DD_STRIKE_CE/PE
            parts = row['id'].split('_')
            if len(parts) >= 6:
                expiry_str = parts[3]  # YYYY-MM-DD
                strike = parts[4]
                opt_type = parts[5]
            else:
                expiry_str = 'Unknown'
                strike = 'N/A'
                opt_type = 'N/A'
            
            # Fallback/cross-check from dispName: "SENSEX 12FEB 74100 CE"
            if ' ' in row['dispName']:
                disp_parts = row['dispName'].split(' ')
                if len(disp_parts) >= 4:
                    short_date = disp_parts[1]  # 12FEB
                    # Convert to YYYY-MM-DD if needed (optional)

            expiries.add(expiry_str)
            
            strikes_by_expiry[expiry_str].append({
                'strike': strike,
                'type': opt_type,
                'token': row['excToken'],
                'dispName': row['dispName'],
                'lot': row['lot'],
                'weekly': row['weekly']
            })

print(f"Total SENSEX weekly options: {len(sensex_rows)}")
print(f"Lot size: {sensex_rows[0]['lot'] if sensex_rows else 'N/A'}")
print(f"Weekly flag: {sensex_rows[0]['weekly'] if sensex_rows else 'N/A'}")

print("\nUnique weekly expiries (Thursdays):")
for exp in sorted(expiries):
    try:
        exp_date = datetime.strptime(exp, '%Y-%m-%d')
        print(f" - {exp} ({exp_date.strftime('%d %b %Y')} - {exp_date.strftime('%A')})")
    except:
        print(f" - {exp} (format issue)")

print("\nStrikes per expiry (with approx ATM):")
for exp, items in sorted(strikes_by_expiry.items()):
    print(f"\n{exp} ({len(items)//2} strike pairs, lot {items[0]['lot']}, weekly '{items[0]['weekly']}'):")
    
    # Sort by strike numeric
    items.sort(key=lambda x: float(x['strike']) if x['strike'].replace('.','').isdigit() else 0)
    
    # Approx ATM = middle strike
    strikes = [float(i['strike']) for i in items if i['strike'].replace('.','').isdigit()]
    if strikes:
        atm_strike = strikes[len(strikes)//2]
        print(f"  Approx ATM strike: {atm_strike} (middle of chain)")
        
        # Show 10 samples around ATM
        start_idx = max(0, len(items)//2 - 5)
        for item in items[start_idx:start_idx+10]:
            print(f"   {item['strike']} {item['type']} → Token: {item['token']} ({item['dispName']})")
        if len(items) > 10:
            print("   ... (full chain in CSV)")

print("\nDone — for real-time ATM, we'll add live SENSEX LTP from streamer next.")