#!/usr/bin/env python3
import requests
import json

response = requests.get('http://localhost:5000/api/signals-data')
data = response.json()

print(f'Total trades: {len(data["trades"])}')

march4_trades = [t for t in data['trades'] if t.get('entry_time', '').startswith('2026-03-04')]
print(f'March 4th trades: {len(march4_trades)}')

if march4_trades:
    print('Sample March 4th trade:')
    print(json.dumps(march4_trades[0], indent=2))
else:
    print('No March 4th trades found')

# Check sell reasons
sell_reasons = set()
for trade in data['trades']:
    if trade.get('sell_reason') and trade['sell_reason'] != 'unknown':
        sell_reasons.add(trade['sell_reason'])

print(f'Unique sell reasons found: {sorted(sell_reasons)}')