import logging
from mono_engine.engine import MonoEngine
import time
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

# --- Add our imports here ---
from datetime import datetime
import csv
import io
import os

from openapi_client import Configuration, ApiClient
from openapi_client.api import SymbolDetailsApi

from mono_engine.modules.sensex_options import SensexOptions
from mono_engine.modules.order import Order
from mono_engine.modules.pnl import PnLModule
#from mono_engine.modules.charting_engine import ChartingEngine


# ======================
# Main Engine Code
# ======================
engine = MonoEngine()

# Call login separately to prompt mode after authentication
if engine.login():
    print("\nChoose trading mode:")
    print("1. real")
    print("2. paper")
    print("3. historical (backtest on DB data)")
    choice = input("Enter 1/2/3 (default: 2 paper): ").strip() or "2"

    if choice == "1":
        mode = "real"
    elif choice == "3":
        mode = "historical"
    else:
        mode = "paper"

    print(f"Selected mode: {mode.upper()}")
    engine.mode = mode

    # Choose stoploss strategy
    print("\nChoose stoploss strategy:")
    print("1. afl (AFL-based dynamic stoploss)")
    print("2. 2percent (2% profit target strategy)")
    strategy_choice = input("Enter 1/2 (default: 1 afl): ").strip() or "1"

    if strategy_choice == "2":
        stoploss_strategy = "2percent"
        print("Selected strategy: 2PERCENT (2% profit target)")
    else:
        stoploss_strategy = "afl"
        print("Selected strategy: AFL (dynamic stoploss)")

    # Update config with selected strategy
    if 'stoploss_params' not in engine.config._raw_data:
        engine.config._raw_data['stoploss_params'] = {}
    engine.config._raw_data['stoploss_params']['strategy'] = stoploss_strategy

    logging.info(f"Engine authenticated — starting in {mode.upper()} mode")

    engine.streamer.start()
    engine._load_modules()

    # ======================
    # HISTORICAL BACKTEST MODE
    # ======================
    if mode == "historical":
        from mono_engine.modules.historical_backtest import HistoricalBacktest
        backtest = HistoricalBacktest(engine)
        backtest.run()
        engine.stop()
        import sys
        sys.exit(0)

    # ======================
    # LIVE / PAPER MODE (All your original code preserved exactly)
    # ======================

    logging.info(f"MonoEngine fully started — {len(engine.modules)} modules loaded in {mode.upper()} mode")

    # ======================
    # PnL Engine (new Module 11)
    # ======================
    print("Loading PnL Engine...")
    pnl_module = PnLModule(engine)
    engine.modules['pnl'] = pnl_module
    pnl_module.start()
    logging.info("✅ PnLModule loaded — per-buy-reason win-rate + 10s table active")

    # ======================
    # Load SensexOptions Module (after other modules for dependencies)
    # ======================
    print("Loading Sensex Options Module...")
    sensex_module = SensexOptions(engine)
    engine.modules['sensex_options'] = sensex_module
    sensex_module.start()

    # After sensex_module.start() — reload watchlist
    market_data = engine.modules.get('market_data')
    if market_data:
        market_data._load_watchlist()

    # === NEW: Charting Engine Integration (your original commented code preserved) ===
    charting_engine = None
    logging.info("ChartingEngine intentionally disabled — no browser charts")

    # ======================
    # BUY_SIGNAL HANDLER (fixed for PaperTrading + StateModule)
    # ======================
    state_module = engine.modules.get('state')
    execution_module = engine.modules.get('execution')

    def handle_buy_signal(data: dict):
        symbol = data.get('symbol') or data.get('subscribed_symbol')
        price = data.get('price')
        qty = data.get('quantity', 900)
        buy_reason = data.get('buy_reason', 'unknown')

        if not symbol or price is None:
            logging.warning("buy_signal missing symbol or price")
            return

        logging.info(f"Received buy_signal for {symbol} @ {price} (reason: {buy_reason})")

        if state_module.is_in_trade(symbol):
            logging.info(f"Already IN_TRADE for {symbol} → ignoring")
            return

        if execution_module:
            try:
                execution_module.place_order(
                    symbol,
                    qty,
                    'buy',
                    order_type='market',
                    price=price,
                    buy_reason=buy_reason
                )
                logging.info(f"✅ BUY ORDER SENT for {symbol} @ {price} (qty={qty}, reason={buy_reason})")
            except Exception as e:
                logging.error(f"Execution failed for {symbol}: {e}")
        else:
            logging.error("No execution module loaded!")

    def handle_exit_signal(data: dict):
        symbol = data.get('symbol') or data.get('subscribed_symbol')
        price = data.get('exit_price')  # Updated field name
        qty = data.get('quantity', 900)
        reason = data.get('reason', 'strategy_exit')

        if not symbol or price is None:
            logging.warning("exit_signal missing symbol or price")
            return

        logging.info(f"Received exit_signal for {symbol} @ {price} (reason: {reason})")

        if execution_module:
            try:
                execution_module.place_order(
                    symbol,
                    qty,
                    'sell',
                    order_type='market',
                    price=price,
                    sell_reason=reason
                )
                logging.info(f"✅ SELL ORDER SENT for {symbol} @ {price} (qty={qty}, reason={reason})")
            except Exception as e:
                logging.error(f"Exit execution failed for {symbol}: {e}")
        else:
            logging.error("No execution module loaded!")

    engine.events.subscribe('buy_signal', handle_buy_signal)
    engine.events.subscribe('exit_signal', handle_exit_signal)
    logging.info("✅ buy_signal handler registered (PaperTrading compatible)")
    logging.info("✅ exit_signal handler registered (PaperTrading compatible)")
    
    # ======================
    # HISTORICAL PNL REPLAY (NEW)
    # ======================
    print("\n" + "="*80)
    run_hist = input("Run Historical PnL Replay now (delta mode)? (y/n): ").strip().lower()
    print("="*80)
    
    if run_hist == 'y':
        from mono_engine.modules.historical_backtest import HistoricalBacktest
        print("🚀 Starting Delta Historical PnL Replay...")
        HistoricalBacktest(engine).run()
        print("✅ Historical PnL Replay Finished!")
    
    # Main loop
    logging.info("Engine running — press Ctrl+C to stop")
    while True:
        time.sleep(0.1)
        market_data = engine.modules.get('market_data')
        if market_data:
            market_data.process_amibroker_queue()

else:
    logging.error("Login failed—exiting.")

# Handle stop on interrupt
try:
    pass
except KeyboardInterrupt:
    engine.stop()