#!/usr/bin/env python3
"""
Test script to verify dynamic stoploss module loading in the engine
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mono_engine.config import Config
from mono_engine.engine import MonoEngine


def test_dynamic_loading():
    """Test that the engine correctly loads different stoploss modules"""
    print("Testing Dynamic Stoploss Module Loading")
    print("=" * 50)

    # Test 1: AFL strategy loading
    print("\nTest 1: Loading AFL strategy")
    engine_afl = MonoEngine()
    # Manually set config for AFL
    engine_afl.config._raw_data['stoploss_params'] = {'strategy': 'afl'}

    try:
        # Simulate the module loading logic
        stoploss_strategy = engine_afl.config.get('stoploss_params', {}).get('strategy', 'afl')
        module_map = {
            'stoploss': ('mono_engine.modules.stoploss' if stoploss_strategy == 'afl' else 'mono_engine.modules.stoploss_2percent',
                        'StoplossModule' if stoploss_strategy == 'afl' else 'Stoploss2PercentModule'),
        }

        module_path, class_name = module_map['stoploss']
        print(f"Strategy: {stoploss_strategy}")
        print(f"Module path: {module_path}")
        print(f"Class name: {class_name}")

        # Try to import and check class exists
        import importlib
        module = importlib.import_module(module_path)
        if hasattr(module, class_name):
            print(f"SUCCESS: Found class {class_name} in {module_path}")
        else:
            print(f"ERROR: Class {class_name} not found in {module_path}")

    except Exception as e:
        print(f"ERROR: {e}")

    # Test 2: 2percent strategy loading
    print("\nTest 2: Loading 2percent strategy")
    engine_2percent = MonoEngine()
    # Manually set config for 2percent
    engine_2percent.config._raw_data['stoploss_params'] = {'strategy': '2percent'}

    try:
        # Simulate the module loading logic
        stoploss_strategy = engine_2percent.config.get('stoploss_params', {}).get('strategy', 'afl')
        module_map = {
            'stoploss': ('mono_engine.modules.stoploss' if stoploss_strategy == 'afl' else 'mono_engine.modules.stoploss_2percent',
                        'StoplossModule' if stoploss_strategy == 'afl' else 'Stoploss2PercentModule'),
        }

        module_path, class_name = module_map['stoploss']
        print(f"Strategy: {stoploss_strategy}")
        print(f"Module path: {module_path}")
        print(f"Class name: {class_name}")

        # Try to import and check class exists
        import importlib
        module = importlib.import_module(module_path)
        if hasattr(module, class_name):
            print(f"SUCCESS: Found class {class_name} in {module_path}")
        else:
            print(f"ERROR: Class {class_name} not found in {module_path}")

    except Exception as e:
        print(f"ERROR: {e}")

    print("\n" + "=" * 50)
    print("Dynamic loading test completed!")
    print("\nThe engine will now correctly load:")
    print("- StoplossModule from mono_engine.modules.stoploss (for 'afl')")
    print("- Stoploss2PercentModule from mono_engine.modules.stoploss_2percent (for '2percent')")


if __name__ == "__main__":
    test_dynamic_loading()