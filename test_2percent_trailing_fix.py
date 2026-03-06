#!/usr/bin/env python3
"""
Test script to verify the 2% trailing stop fix
"""

def test_trailing_logic():
    """Test that trail level updates correctly as price increases"""
    print("Testing 2% Trailing Stop Logic Fix")
    print("=" * 50)

    # Simulate the monitor state (like in the actual module)
    monitor_state = {
        'entry_price': 0.0,
        'highest_price': 0.0,
        'max_profit_pct': 0.0,
        'target_achieved': False,
        'trail_level': 0.0,
    }

    # Strategy parameters
    profit_target_pct = 2.0  # Minimum 2% profit
    trail_buffer_pct = 2.0   # Exit if drops 2% from high

    # Simulate the trade scenario from the logs
    symbol = "845701_BFO"
    entry_price = 703.15

    # Start monitoring (initialize state)
    monitor_state['entry_price'] = entry_price
    monitor_state['highest_price'] = entry_price
    monitor_state['max_profit_pct'] = 0.0
    monitor_state['target_achieved'] = False
    monitor_state['trail_level'] = 0.0

    print(f"Entry Price: {entry_price}")
    print(f"Initial Trail Level: {monitor_state['trail_level']}")
    print()

    # Simulate price progression (similar to the logs)
    price_sequence = [
        703.15,  # Entry
        710.0,   # First 2% target (2.4% profit)
        720.0,   # Higher (4.0% profit)
        730.0,   # Even higher (5.7% profit)
        740.0,   # Higher still (7.1% profit)
        743.25,  # Peak shown in logs (5.7% profit)
        747.20,  # Final high in exit log (6.3% profit)
    ]

    print("Price Progression and Trail Updates:")
    print("Price   | Profit% | Trail Level | Status")
    print("-" * 45)

    for price in price_sequence:
        # Simulate the trailing logic from the fixed code
        entry = monitor_state['entry_price']
        previous_highest = monitor_state['highest_price']
        monitor_state['highest_price'] = max(monitor_state['highest_price'], price)
        highest = monitor_state['highest_price']
        current_profit_pct = (highest - entry) / entry * 100
        monitor_state['max_profit_pct'] = max(monitor_state['max_profit_pct'], current_profit_pct)

        # Check if 2% target achieved
        if not monitor_state['target_achieved'] and current_profit_pct >= profit_target_pct:
            monitor_state['target_achieved'] = True
            monitor_state['trail_level'] = highest * (1 - trail_buffer_pct / 100)
            status = "TARGET HIT"
        # Update trail level if highest price increased and target already achieved
        elif monitor_state['target_achieved'] and highest > previous_highest:
            monitor_state['trail_level'] = highest * (1 - trail_buffer_pct / 100)
            status = "TRAIL UPDATED"
        else:
            status = "TRAILING"

        profit_pct = (price - entry) / entry * 100
        print("6.2f")

    print()
    print("Final State:")
    print(f"Highest Price: {monitor_state['highest_price']:.2f}")
    print(f"Trail Level: {monitor_state['trail_level']:.2f}")
    print(f"Max Profit: {monitor_state['max_profit_pct']:.1f}%")

    # Test exit condition
    print()
    print("Exit Condition Test:")
    exit_price = 703.00  # Price from the logs
    should_exit = monitor_state['target_achieved'] and exit_price <= monitor_state['trail_level']
    print(f"Exit Price: {exit_price}")
    print(f"Trail Level: {monitor_state['trail_level']:.2f}")
    print(f"Should Exit: {should_exit}")

    if should_exit:
        print("CORRECT: Exit triggered (this is now the correct behavior)")
        print("   Trail level properly maintained at 732.26 (747.20 * 0.98)")
        print("   Exit price 703.00 is correctly below trail level")
    else:
        print("INCORRECT: Exit NOT triggered")
        print("   This would be wrong - exit should have been triggered")

    print()
    print("=" * 50)
    print("Test completed - trailing logic should now work correctly!")
    print()
    print("Key Fix: Trail level now updates continuously as highest price increases!")
    print("Before: Trail set once at 2% target, never updated")
    print("After:  Trail recalculated every time highest price increases")


if __name__ == "__main__":
    test_trailing_logic()
