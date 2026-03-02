# =====================================================
# run_historical_pnl.py
# Standalone Historical PnL Replay (Delta + Full Event Chain)
# Run this anytime — completely independent of run_engine.py
# =====================================================

import logging
import time
import sqlite3
import pandas as pd
from datetime import datetime
from tabulate import tabulate
from mono_engine.engine import MonoEngine
from mono_engine.modules.historical_backtest_old import HistoricalBacktest

# Setup logging exactly like your main engine
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("=" * 90)
    print("🚀 MoNo Engine — Standalone Historical PnL Replay (Delta Mode)")
    print("=" * 90)

    engine = MonoEngine()

    # Login (same as run_engine.py)
    if not engine.login():
        print("❌ Login failed. Exiting.")
        return

    # Force paper mode for safety
    engine.mode = 'paper'
    print("Selected mode: PAPER (Historical replay)")

    # Start streamer (needed for MarketData)
    engine.streamer.start()

    # Load only the modules needed for historical replay
    print("Loading required modules for historical PnL...")
    engine._load_modules()                    # loads state, strategy, market_data, stoploss, pnl, execution (paper)

    # Force-load market_data if it failed
    if 'market_data' not in engine.modules:
        from mono_engine.modules.market_data import MarketData
        md = MarketData(engine)
        engine.modules['market_data'] = md
        md.start()

    # Make sure PnL is in the modules
    if 'pnl' not in engine.modules:
        from mono_engine.modules.pnl import PnLModule
        pnl_module = PnLModule(engine)
        engine.modules['pnl'] = pnl_module
        pnl_module.start()

    # Load SensexOptions + watchlist (required for symbols)
    from mono_engine.modules.sensex_options import SensexOptions
    sensex_module = SensexOptions(engine)
    engine.modules['sensex_options'] = sensex_module
    sensex_module.start()

    # Refresh market_data watchlist
    market_data = engine.modules.get('market_data')
    if market_data:
        market_data._load_watchlist()

    print(f"✅ Engine ready — {len(engine.modules)} modules loaded")
    print("Starting Delta Historical PnL Replay...")

    # Run the historical backtest (delta + full PnL)
    backtest = HistoricalBacktest(engine)
    backtest.run()

    print("\n" + "="*90)
    print("✅ Standalone Historical PnL Replay Completed!")
    print("Check the table above + mono_engine_data.db → trades table")
    print("="*90)

    # Keep script alive for a few seconds so you can see the table
    time.sleep(5)


if __name__ == "__main__":
    main()