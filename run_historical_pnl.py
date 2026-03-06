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
from mono_engine.modules.historical_backtest import HistoricalBacktest

# Setup logging exactly like your main engine
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("=" * 90)
    print("MoNo Engine - Standalone Historical PnL Replay (Delta Mode)")
    print("=" * 90)

    engine = MonoEngine()

    # Skip login for historical backtest - use offline mode
    print("Running in OFFLINE HISTORICAL mode (no login required)")
    engine.mode = 'historical'

    # Load only the core modules needed for historical replay
    print("Loading required modules for historical PnL...")
    # Load core modules manually to avoid win32com dependency
    from mono_engine.modules.state import StateModule
    from mono_engine.modules.stoploss import StoplossModule
    from mono_engine.modules.pnl import PnLModule
    from mono_engine.modules.order import Order
    import sys
    sys.path.append('mono_engine/strategies')
    from strategy import StrategyModule

    # Initialize core modules
    state_module = StateModule(engine)
    stoploss_module = StoplossModule(engine)
    pnl_module = PnLModule(engine)
    order_module = Order(engine)
    # Use 1min timeframe for historical backtest to avoid resampling issues
    strategy_module = StrategyModule(engine)

    # Add to engine modules
    engine.modules['state'] = state_module
    engine.modules['stoploss'] = stoploss_module
    engine.modules['pnl'] = pnl_module
    engine.modules['order'] = order_module
    engine.modules['strategy'] = strategy_module

    # Start modules
    state_module.start()
    stoploss_module.start()
    pnl_module.start()
    order_module.start()
    strategy_module.start()

    print(f"[OK] Engine ready — {len(engine.modules)} modules loaded")
    print("Starting Delta Historical PnL Replay...")

    # Run the historical backtest (delta + full PnL)
    backtest = HistoricalBacktest(engine)
    backtest.run()

    print("\n" + "="*90)
    print("[OK] Standalone Historical PnL Replay Completed!")
    print("Check the table above + mono_engine_data.db -> trades table")
    print("="*90)

    # Keep script alive for a few seconds so you can see the table
    time.sleep(5)


if __name__ == "__main__":
    main()