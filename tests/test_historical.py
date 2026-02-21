# tests/test_historical.py - Standalone test for Tradejini historical candles

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to path

from mono_engine.config import Config
from mono_engine.core.session import Session
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_historical_candle():
    print("Starting standalone historical candle test...")
    
    # Load your config (same as engine)
    config = Config.load('config.yaml')
    
    # Force fresh 2FA prompt
    two_fa = input("\nEnter CURRENT 6-digit 2FA code (generate fresh now!): ").strip()
    if two_fa:
        config.credentials['two_fa'] = two_fa
        config.credentials['two_fa_typ'] = 'totp'
        logging.info("Using fresh 2FA from prompt")
    else:
        print("No 2FA entered — login may fail.")
    
    # Create session and login
    session = Session(config)
    if not session.login():
        print("Login failed — cannot test historical data.")
        return
    
    print("Login successful — access token:", session.access_token)
    
    # Example: Pull 1min candles for one watchlist symbol
    #symbol_token = '1163955_BFO'  # Your CE token example from log
    #symbol_token = 'IDX_-51_BSE'  # Your CE token example from log
    symbol_token = 'OPTIDX_SENSEX_BFO_2026-02-26_82300_CE'  # Your CE token example from log
    # Time range: last 1 day (adjust as needed)
    to_time = int(datetime.now().timestamp())
    from_time = to_time - (86400 * 1)  # 1 day ago
    
    params = {
        'id': symbol_token,
        'interval': '1',
        'from': from_time,
        'to': to_time,
        'exchange': 'BSE'  # Try this if id alone fails
    }
    
    print(f"Requesting historical 1min candles for {params['id']}")
    print(f"From: {datetime.fromtimestamp(from_time)}")
    print(f"To:   {datetime.fromtimestamp(to_time)}")
    
    try:
        response = session.rest.get("/api/mkt-data/chart/interval-data", params=params)
        print("\nSUCCESS — Historical data received!")
        print("Response keys:", list(response.keys()))
        if 'd' in response and 'bars' in response['d']:
            bars = response['d']['bars']
            print(f"Number of 1min bars: {len(bars)}")
            if bars:
                first = bars[0]
                last = bars[-1]
                print("First candle (ts, o, h, l, c, v):", first)
                print("Last candle (ts, o, h, l, c, v):", last)
                # Convert first ts to readable date
                first_ts = datetime.fromtimestamp(first[0]/1000)  # ms to sec
                last_ts = datetime.fromtimestamp(last[0]/1000)
                print("First timestamp:", first_ts)
                print("Last timestamp:", last_ts)
        else:
            print("No bars in response — full response:")
            print(response)
    except Exception as e:
        print("Historical request failed:")
        print(str(e))
        if hasattr(e, 'response') and e.response is not None:
            print("Response text:", e.response.text)
    # ... after historical success ...

    # Test Greeks for the same symbol
    print("\nTesting Greeks for the same symbol...")
    greeks_params = {
        'id': symbol_token  # full ID
    }
    try:
        greeks_response = session.rest.get("/api/mkt-data/option-greeks", params=greeks_params)
        print("Greeks SUCCESS!")
        print("Greeks response:", greeks_response)
    except Exception as e:
        print("Greeks request failed:", str(e))
        if hasattr(e, 'response') and e.response is not None:
            print("Greeks response text:", e.response.text)

    # Test Depth (L5 snapshot)
    print("\nTesting Depth (L5) for the same symbol...")
    depth_params = {
        'id': symbol_token,
        'level': '5'  # or '2' for L2
    }
    try:
        depth_response = session.rest.get("/api/mkt-data/depth", params=depth_params)
        print("Depth SUCCESS!")
        print("Depth response:", depth_response)
    except Exception as e:
        print("Depth request failed:", str(e))
        if hasattr(e, 'response') and e.response is not None:
            print("Depth response text:", e.response.text)
    session.close()
    print("\nTest complete.")

if __name__ == "__main__":
    test_historical_candle()