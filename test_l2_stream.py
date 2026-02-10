import logging
import sys
import time
from datetime import datetime
from pytz import timezone
from tabulate import tabulate  # For tabular output

# Fix for import path: Add current directory to sys.path
sys.path.insert(0, '.')  # This ensures Python can find mono_engine from C:\MoNo_Engine

try:
    from mono_engine.engine import MonoEngine  # Correct class name from engine.py
    from mono_engine.core.events import EVENT_TICK, EVENT_CONNECT  # Events from core/events.py
except ModuleNotFoundError as e:
    logging.error(f"Import failed: {e}. Verify folder names are lowercase and files exist as per dir output.")
    sys.exit(1)

# Setup logging to see outputs clearly
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def on_connect(*args):
    try:
        logging.info("Streamer connected — subscribing to test symbols")
        # Use your real BFO option tokens from output/logs (valid for L2)
        test_symbols = ['831199_BFO', '831435_BFO', '831669_BFO', '-51_BSE']  # Options + spot (spot won't have L2)
        engine.streamer.subscribeL1(test_symbols)
        engine.streamer.subscribeL2SnapShot(test_symbols)  # Snapshot for initial L2
        engine.streamer.subscribeL2(test_symbols)  # Ongoing L2 updates
        logging.info(f"Subscribed to L1, L2 Snapshot, and L2 for: {test_symbols}")
    except AttributeError as e:
        logging.error(f"Subscription error in on_connect: {e}. Check SDK method names (e.g., subscribeL2SnapShot).")

def on_tick(tick):
    symbol = tick.get('symbol', 'N/A')
    now_ist = datetime.now(timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    
    # Print full raw tick for debugging
    logging.info(f"[{now_ist}] Full raw tick for {symbol}: {tick}")
    
    # Prepare basic table data (L1 fields)
    ltt = tick.get('ltt', 'N/A')
    ltp = tick.get('ltp', 'N/A')
    chng = tick.get('chng', 'N/A')
    chngPer = tick.get('chngPer', 'N/A')
    open_val = tick.get('open', 'N/A')
    high = tick.get('high', 'N/A')
    low = tick.get('low', 'N/A')
    close = tick.get('close', 'N/A')
    vol = tick.get('vol', 'N/A')
    oi = tick.get('OI', 'N/A')
    bidPrice = tick.get('bidPrice', 'N/A')
    askPrice = tick.get('askPrice', 'N/A')
    qty = tick.get('qty', 'N/A')
    totBuyQty = tick.get('totBuyQty', 'N/A')
    totSellQty = tick.get('totSellQty', 'N/A')

    row = [
        [symbol, ltt, ltp, chng, chngPer, f"{open_val}/{high}/{low}/{close}", vol, oi, f"{bidPrice}x{qty}", f"{askPrice}x{qty}", f"Bids: {totBuyQty} | Asks: {totSellQty}"]
    ]

    headers = ["Symbol", "Last Time", "LTP", "Change", "% Change", "OHLC", "Volume", "OI", "Best Bid", "Best Ask", "Depth"]

    # Print basic table
    print(f"\n=== Updated Tick Data ({now_ist}) ===")
    print(tabulate(row, headers=headers, tablefmt="grid"))

    # If L2 packet (has 'bid' and 'ask' lists), print full depth table
    if 'bid' in tick and isinstance(tick['bid'], list) and tick['bid']:
        bid_table = [[b.get('price', 'N/A'), b.get('qty', 'N/A'), b.get('no', 'N/A')] for b in tick['bid']]
        ask_table = [[a.get('price', 'N/A'), a.get('qty', 'N/A'), a.get('no', 'N/A')] for a in tick['ask']]
        
        print(f"\n=== Full L2 Bid Depth for {symbol} ({now_ist}) ===")
        print(tabulate(bid_table, headers=["Bid Price", "Bid Qty", "Bid Orders"], tablefmt="grid"))
        
        print(f"\n=== Full L2 Ask Depth for {symbol} ({now_ist}) ===")
        print(tabulate(ask_table, headers=["Ask Price", "Ask Qty", "Ask Orders"], tablefmt="grid"))
        
        logging.info(f"L2 Depth data detected for {symbol}: Total Bids {totBuyQty}, Total Asks {totSellQty}")

# Initialize the engine
try:
    engine = MonoEngine()  # Adapt if needed
except Exception as e:
    logging.error(f"Engine initialization failed: {e}. Check if login/auth is set up correctly.")
    sys.exit(1)

# Subscribe to events
engine.events.subscribe(EVENT_CONNECT, on_connect)
engine.events.subscribe(EVENT_TICK, on_tick)

# Start the engine and streamer
logging.info("Starting engine for L2 test...")
engine.start()

# Let it run for 300 seconds (5 min) to capture ticks during market
try:
    time.sleep(300)
except KeyboardInterrupt:
    logging.info("Interrupted by user")

# Stop the engine cleanly
logging.info("Stopping engine...")
engine.stop()