import requests
import json

try:
    response = requests.get('http://127.0.0.1:5000/api/signals-data')
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.text[:500]}")

    data = response.json()
    print(f"Keys in response: {list(data.keys())}")

    trades = data.get('trades', [])
    completed_trades = [t for t in trades if t.get('exit_time')]

    print(f"Total trades: {len(trades)}, Completed: {len(completed_trades)}")

    if completed_trades:
        total_pnl = sum(t.get('realized_pnl', 0) for t in completed_trades)
        print(f"Total PnL: {total_pnl:,.0f}")

        print("Sample trade:")
        print(json.dumps(completed_trades[0], indent=2, default=str))

        # Check sell reasons
        sell_reasons = [t.get('sell_reason') for t in completed_trades if t.get('sell_reason')]
        print(f"Sell reasons found: {len(sell_reasons)}")
        print(f"Unique sell reasons: {set(sell_reasons)}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
