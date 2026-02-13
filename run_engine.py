import logging
from mono_engine.engine import MonoEngine
import time

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

    # After sensex_module.start()
    market_data = engine.modules.get('market_data')
    if market_data:
        market_data._load_watchlist()  # Reload after addition

    # Temp: Get watchlist from market_data and simulate buy signals
    market_data = engine.modules.get('market_data')
    if market_data and market_data.watchlist:
        for item in market_data.watchlist:  # Loop over watchlist
            symbol = item['symbol']
            qty = 900 if engine.mode == 'paper' else 1  # Paper qty placeholder
            # Publish signal (mimics strategy)
            engine.events.publish('buy_signal', {'symbol': symbol, 'quantity': qty, 'order_type': 'market'})
            time.sleep(1)  # Delay for processing
    else:
        print("No watchlist—load first.")

    # Temp: Simulate sell signal for first watchlist item (for PnL test)
    state = engine.modules.get('state')
    if state.is_in_trade() and market_data.watchlist:
        first_symbol = market_data.watchlist[0]['symbol']
        engine.events.publish('sell_signal', {'symbol': first_symbol})
        time.sleep(1)

    # Temp loop
    market_data = engine.modules.get('market_data')
    if market_data and market_data.watchlist:
        market_data._load_watchlist()  # Reload
        for item in market_data.watchlist:
            token_symbol = f"{item['token']}_BFO"  # For quotes
            disp_symbol = item['symbol']  # For logs
            qty = 900 if engine.mode == 'paper' else 1
            engine.events.publish('buy_signal', {'symbol': disp_symbol, 'token_symbol': token_symbol, 'quantity': qty, 'order_type': 'market'})
            time.sleep(10)  # Longer delay for ticks
    else:
        print("No watchlist—load first.")

    if state.is_in_trade() and market_data.watchlist:
        first_item = market_data.watchlist[0]
        first_disp = first_item['symbol']
        first_token = f"{first_item['token']}_BFO"
        engine.events.publish('sell_signal', {'symbol': first_disp, 'token_symbol': first_token})
        time.sleep(10)

     
    # Main loop
    logging.info("Engine running — press Ctrl+C to stop")
    while True:
        time.sleep(1)
else:
    logging.error("Login failed—exiting.")

# Handle stop on interrupt
try:
    pass  # Loop above handles
except KeyboardInterrupt:
    engine.stop()