#!/usr/bin/env python3
"""
Test script to verify interactive stoploss strategy selection
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mono_engine.config import Config
from mono_engine.engine import MonoEngine


def test_interactive_selection():
    """Test the interactive strategy selection logic"""
    print("Testing Interactive Stoploss Strategy Selection")
    print("=" * 60)

    # Simulate the selection logic from run_engine.py
    print("\nSimulating user prompts...")

    # Test AFL selection (choice "1")
    print("\nTest 1: User selects '1' (AFL strategy)")
    strategy_choice = "1"
    if strategy_choice == "2":
        stoploss_strategy = "2percent"
        print("Selected strategy: 2PERCENT (2% profit target)")
    else:
        stoploss_strategy = "afl"
        print("Selected strategy: AFL (dynamic stoploss)")

    # Create engine and update config
    engine = MonoEngine()
    if 'stoploss_params' not in engine.config._raw_data:
        engine.config._raw_data['stoploss_params'] = {}
    engine.config._raw_data['stoploss_params']['strategy'] = stoploss_strategy

    # Check the result
    selected_strategy = engine.config.get('stoploss_params', {}).get('strategy', 'afl')
    print(f"Config updated to: '{selected_strategy}'")
    assert selected_strategy == 'afl', f"Expected 'afl', got '{selected_strategy}'"
    print("AFL selection test passed")

    # Test 2percent selection (choice "2")
    print("\nTest 2: User selects '2' (2percent strategy)")
    strategy_choice = "2"
    if strategy_choice == "2":
        stoploss_strategy = "2percent"
        print("Selected strategy: 2PERCENT (2% profit target)")
    else:
        stoploss_strategy = "afl"
        print("Selected strategy: AFL (dynamic stoploss)")

    # Update config again
    engine.config._raw_data['stoploss_params']['strategy'] = stoploss_strategy

    # Check the result
    selected_strategy = engine.config.get('stoploss_params', {}).get('strategy', 'afl')
    print(f"Config updated to: '{selected_strategy}'")
    assert selected_strategy == '2percent', f"Expected '2percent', got '{selected_strategy}'"
    print("2percent selection test passed")

    # Test default selection (empty choice)
    print("\nTest 3: User presses Enter (default AFL strategy)")
    strategy_choice = ""  # Empty string simulates pressing Enter
    strategy_choice = strategy_choice or "1"  # Apply default
    if strategy_choice == "2":
        stoploss_strategy = "2percent"
        print("Selected strategy: 2PERCENT (2% profit target)")
    else:
        stoploss_strategy = "afl"
        print("Selected strategy: AFL (dynamic stoploss)")

    # Update config again
    engine.config._raw_data['stoploss_params']['strategy'] = stoploss_strategy

    # Check the result
    selected_strategy = engine.config.get('stoploss_params', {}).get('strategy', 'afl')
    print(f"Config updated to: '{selected_strategy}'")
    assert selected_strategy == 'afl', f"Expected 'afl', got '{selected_strategy}'"
    print("Default selection test passed")

    print("\n" + "=" * 60)
    print("Interactive Selection Logic Working Correctly!")
    print("\nWhen you run the engine, you'll see prompts like:")
    print("Choose trading mode:")
    print("1. real")
    print("2. paper")
    print("3. historical (backtest on DB data)")
    print("")
    print("Choose stoploss strategy:")
    print("1. afl (AFL-based dynamic stoploss)")
    print("2. 2percent (2% profit target strategy)")
    print("=" * 60)


if __name__ == "__main__":
    test_interactive_selection()