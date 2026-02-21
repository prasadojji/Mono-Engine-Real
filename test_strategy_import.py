# test_strategy_import.py (in project root)
import sys
print(sys.path)  # to see paths

try:
    from mono_engine.strategies.strategy import StrategyModule
    print("SUCCESS: StrategyModule imported")
except ImportError as e:
    print("Import failed:", e)