"""
test_sensex_search.py

Purpose:
- Test login using your existing Session class (direct REST auth)
- Attempt to fetch historical 1-minute OHLCV data for BSE Sensex index
- Using the authenticated RestClient (no ShoonyaApi-py needed yet)

Run with:
python test_sensex_search.py
"""

import logging
import sys
import datetime
import time
from mono_engine.config import Config
from mono_engine.core.session import Session

# Set up logging (matches your other scripts)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("=== Mono Engine - Sensex Historical Data Test ===")
    print("Loading config and creating session...")

    # Load configuration
    config = Config.load('config.yaml')
    session = Session(config)

    # Prompt for fresh 2FA (TOTP) code
    two_fa_input = input("\nEnter FRESH 6-digit 2FA code (generate now!): ").strip()
    if two_fa_input:
        session.config.credentials['two_fa'] = two_fa_input
    else:
        print("Warning: No 2FA provided. Login may fail if required.")

    # Attempt login
    if not session.login():
        print("Login failed — check credentials, 2FA, or config.yaml")
        sys.exit(1)

    print("\nLOGIN SUCCESSFUL!")
    print("Access Token (partial):", session.access_token[:20] + "..." if session.access_token else "None")
    print("Rest base URL:", session.rest.base_url)

    # --- Historical Data Fetch Section ---
    rest = session.rest

    # Tradejini historical interval data endpoint (confirmed from API docs/forums)
    HIST_ENDPOINT = "/api/mkt-data/chart/interval-data"

    # Sensex symbol IDs to try (common formats - adjust based on error response)
    possible_symbol_ids = [
        "SENSEX_BSE",
        "IDX_SENSEX_BSE",
        "SENSEX",
        "BSE_SENSEX",
        "26000",  # BSE token for Sensex (sometimes accepted)
        "IDX_BSE:SENSEX"
    ]

    # Time range: last 5 days (small test - increase later)
    now_unix = int(time.time())
    five_days_ago_unix = now_unix - (5 * 24 * 3600)

    print("\n=== Attempting historical 1-min data fetch for Sensex ===")
    print(f"Time range: {datetime.datetime.fromtimestamp(five_days_ago_unix)} → {datetime.datetime.fromtimestamp(now_unix)}")

    found = False
    for symbol_id in possible_symbol_ids:
        params = {
            "id": symbol_id,
            "from": str(five_days_ago_unix),
            "to": str(now_unix),
            "interval": "1"  # 1 = 1-minute candles
        }

        print(f"\nTrying symbol ID: {symbol_id}")
        print("Params:", params)

        try:
            response = rest.get(HIST_ENDPOINT, params=params)
            print("SUCCESS! Response received.")

            # Print response structure
            print("Response type:", type(response))
            if isinstance(response, dict):
                print("Keys in response:", list(response.keys()))
                if 'data' in response:
                    candles = response['data']
                    print(f"Fetched {len(candles)} candles")
                    if candles:
                        print("First candle:", candles[0])
                        print("Last candle:", candles[-1])
                elif 'error' in response or 'message' in response:
                    print("API returned error:", response)
                else:
                    print("Full response:", response)

            elif isinstance(response, list):
                print(f"Fetched {len(response)} candles")
                if response:
                    print("First candle:", response[0])
                    print("Last candle:", response[-1])
            else:
                print("Unexpected response format:", response)

            found = True
            break  # Stop after first successful attempt

        except Exception as e:
            print(f"Failed for {symbol_id}: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_body = e.response.json()
                    print("Error response body:", error_body)
                except:
                    print("Raw response text:", e.response.text)
            print("-" * 60)

    if not found:
        print("\nNone of the symbol IDs worked.")
        print("Next steps:")
        print("1. Check Tradejini API docs / support for exact 'id' format for BSE SENSEX index")
        print("2. Try getting scrip master first (endpoint like /scrip-master or /instruments)")
        print("   Example: rest.get('/api/mkt-data/scrip-master') or similar")
        print("3. Or integrate ShoonyaApiPy for easier get_time_price_series() method")

    print("\nTest complete.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)