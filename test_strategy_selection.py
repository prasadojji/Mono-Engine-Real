#!/usr/bin/env python3
"""
Test script to verify stoploss strategy selection and dynamic loading
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mono_engine.config import Config
from mono_engine.engine import MonoEngine


def test_strategy_selection():
    """Test that strategy selection works correctly"""
    print("Testing Stoploss Strategy Selection")
    print("=" * 50)

    # Test actual module loading
    print("\n1. Testing actual module loading:")

    # Test AFL loading
    try:
        from mono_engine.modules.stoploss import StoplossModule
        print("   OK: AFL module (StoplossModule) can be imported")
    except ImportError as e:
        print(f"   ERROR: AFL module import failed: {e}")

    # Test 2percent loading
    try:
        from mono_engine.modules.stoploss_2percent import Stoploss2PercentModule
        print("   OK: 2percent module (Stoploss2PercentModule) can be imported")
    except ImportError as e:
        print(f"   ERROR: 2percent module import failed: {e}")

    print("\n2. Current config setting:")
    current_config = Config.load('config.yaml')

    # Debug: check what attributes the config has
    print(f"   Config attributes: {[attr for attr in dir(current_config) if not attr.startswith('_')]}")

    # Check if stoploss_params exists at root level
    if hasattr(current_config, 'stoploss_params'):
        stoploss_params = current_config.stoploss_params
        current_strategy = stoploss_params.get('strategy', 'afl') if isinstance(stoploss_params, dict) else 'afl'
        print(f"   Found stoploss_params as attribute: {stoploss_params}")
    else:
        # Try the get method
        stoploss_params = current_config.get('stoploss_params', {})
        current_strategy = stoploss_params.get('strategy', 'afl') if isinstance(stoploss_params, dict) else 'afl'
        print(f"   Found stoploss_params via get(): {stoploss_params}")

    print(f"   Current strategy in config.yaml: '{current_strategy}'")

    if current_strategy == 'afl':
        print("   Will load: StoplossModule (AFL strategy)")
    elif current_strategy == '2percent':
        print("   Will load: Stoploss2PercentModule (2% profit strategy)")
    else:
        print(f"   Unknown strategy '{current_strategy}' - will default to AFL")

    print("\n3. How to switch strategies:")
    print("   Edit config.yaml and change:")
    print("   stoploss_params:")
    print("     strategy: 'afl'        # For AFL strategy")
    print("     # OR")
    print("     strategy: '2percent'   # For 2% profit strategy")

    print("\n4. Strategy versions for backtesting:")
    buy_version = current_config.get('strategy_versions', {}).get('buy_version', 'unknown')
    sell_version = current_config.get('strategy_versions', {}).get('sell_version', 'unknown')
    print(f"   Buy version: {buy_version}")
    print(f"   Sell version: {sell_version}")

    print("\nStrategy selection test completed!")


if __name__ == "__main__":
    test_strategy_selection()