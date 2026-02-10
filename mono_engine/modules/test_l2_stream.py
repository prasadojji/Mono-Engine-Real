import logging
import time
from datetime import datetime
from pytz import timezone

# Assuming your engine imports (adapt paths if needed)
from mono_engine.core.engine import Engine  # Or wherever your main Engine class is
from mono_engine.core.events import EVENT_TICK, EVENT_CONNECT

# Setup logging
logging.basicConfig(level=logging.INFO)

def on_connect(*args):
    logging.info("Streamer connected — subscribing to test symbols")
    # Test symbols: SENSEX spot + one option (adapt token from your watchlist)
    test_symbols = ['-51_BSE', '84500_BFO']  # Format: token_exchange
    streamer.subscribe_l1(test_symbols)
    streamer.subscribe_l2(test_symbols)  # Key: Subscribe to L2
    logging.info(f"Subscribed to L1/L2 for: {test_symbols}")

def on_tick(tick):
    symbol = tick.get('symbol', 'N/A')
    now_ist = datetime.now(timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"[{now_ist}] Tick for {symbol}: {tick}")
    # Check specific L2 fields
    depth_info = {
        'bidPrice': tick.get('bidPrice', 'N/A'),
        'askPrice': tick.get('askPrice', 'N/A'),
        'qty': tick.get('qty', 'N/A'),  # Bid/ask quantity
        'totBuyQty': tick.get('totBuyQty', 'N/A'),
        'totSellQty': tick.get('totSellQty', 'N/A')
    }
    if any(v != 'N/A' for v in depth_info.values()):
        logging.info(f"L2 Depth detected for {symbol}: {depth_info}")
    else:
        logging.info(f"No L2 Depth yet for {symbol} (expected off-hours)")

# Initialize engine (assuming it handles login/auth/streamer setup)
engine = Engine()  # Adapt if your Engine needs config/params
engine.events.subscribe(EVENT_CONNECT, on_connect)
engine.events.subscribe(EVENT_TICK, on_tick)

# Start engine/streamer
engine.start()

# Run for 60 seconds (or longer during market) to capture ticks
try:
    time.sleep(60)  # Adjust duration
except KeyboardInterrupt:
    pass

# Cleanup
engine.stop()