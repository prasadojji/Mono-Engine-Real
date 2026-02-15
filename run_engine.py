import logging
from mono_engine.engine import MonoEngine
import time
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

# --- Add our imports here ---
# These are for the SENSEX logic (datetime for expiry, csv/io for parsing symbols, os for file checks)
from datetime import datetime
import csv
import io
import os

# Broker SDK for public symbols (to fetch Index/BSEOptions CSV if missing — no login needed)
from openapi_client import Configuration, ApiClient
from openapi_client.api import SymbolDetailsApi

# Import our new module (the sensex_options.py you created)
from mono_engine.modules.sensex_options import SensexOptions
from mono_engine.modules.order import Order  # For your test order (optional now, since conditional)
from mono_engine.modules.charting_engine import ChartingEngine


# ======================
# Updated Code for Mode Prompt and Integration
# ======================
engine = MonoEngine()

# Call login separately to prompt mode after authentication
if engine.login():
    # Prompt for mode after successful login
    mode = input("\nChoose trading mode: 'real' or 'paper'? (default: real): ").strip().lower() or 'real'
    if mode not in ['real', 'paper']:
        print("Invalid mode—defaulting to real.")
        mode = 'real'
    print(f"Selected mode: {mode.upper()}")

    # Set mode on engine for conditional loading
    engine.mode = mode

    # Start the rest: streamer, modules (conditional execution loaded in _load_modules)
    logging.info("Engine authenticated — starting streamer and modules")
    engine.streamer.start()
    engine._load_modules()  # Loads modules, including conditional execution
    logging.info(f"MonoEngine fully started — {len(engine.modules)} modules loaded in {mode.upper()} mode")

    # ======================
    # Load SensexOptions Module (after other modules for dependencies)
    # ======================
    print("Loading Sensex Options Module...")
    sensex_module = SensexOptions(engine)  # Create instance
    engine.modules['sensex_options'] = sensex_module  # Add to dict
    sensex_module.start()  # Run grid, selection, subscriptions

    # After sensex_module.start() — reload watchlist to get latest selection
    market_data = engine.modules.get('market_data')
    if market_data:
        market_data._load_watchlist()  # Ensure we have the fresh watchlist after user selection

    # === NEW: Charting Engine Integration (relaxed condition — spot_token can be set later on tick) ===
    market_data = engine.modules.get('market_data')
    state_module = engine.modules.get('state')
    if market_data and state_module and market_data.watchlist:
        charting_engine = ChartingEngine(
            market_data=market_data,
            state_trade_object=state_module.state,  # Pass the inner TradeState object
            timeframes=["1min", "5min"],
            visible_candles=300
        )
        logging.info("ChartingEngine initialized — chart will start plotting when spot token & ticks arrive")
    else:
        logging.error("Cannot start charting — missing market_data (%s), state (%s), or watchlist (len=%s)",
                      market_data is not None,
                      state_module is not None,
                      len(market_data.watchlist) if market_data else 0)
        charting_engine = None

    # === TEMP: Simulate buy/sell signals for testing (uncomment when ready to test paper fills & markers) ===
    # state = engine.modules.get('state')
    # if state and market_data and market_data.watchlist:
    #     logging.info("Running temp buy signals for watchlist items...")
    #     for item in market_data.watchlist:
    #         token_symbol = f"{item['token']}_BFO"
    #         disp_symbol = item['symbol']
    #         qty = 900 if engine.mode == 'paper' else 1
    #         engine.events.publish('buy_signal', {
    #             'symbol': disp_symbol,
    #             'subscribed_symbol': token_symbol,  # Correct key for paper_trading
    #             'quantity': qty,
    #             'order_type': 'market'
    #         })
    #         time.sleep(2)  # Small delay between signals
    #
    #     # Optional: Simulate a sell after delay
    #     time.sleep(10)
    #     if market_data.watchlist:
    #         first_item = market_data.watchlist[0]
    #         engine.events.publish('sell_signal', {
    #             'symbol': first_item['symbol'],
    #             'subscribed_symbol': f"{first_item['token']}_BFO"
    #         })
    # else:
    #     logging.warning("Skipping temp signals — state or watchlist not ready")

    # Main loop
    logging.info("Engine running — press Ctrl+C to stop")
    while True:
        time.sleep(1)
        if charting_engine:
            charting_engine.update()  # Refresh chart every second (builds/plots candles + markers when data ready)
else:
    logging.error("Login failed—exiting.")

# Handle stop on interrupt
try:
    pass  # Loop above handles
except KeyboardInterrupt:
    engine.stop()