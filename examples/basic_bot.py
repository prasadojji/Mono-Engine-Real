import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from datetime import datetime


# examples/basic_bot.py
"""Simple test script for MonoEngine integration."""
from mono_engine.engine import MonoEngine

engine = MonoEngine()
if engine.start():
    # Wait for streamer/modules to init (simulates runtime)
    time.sleep(5)  # Adjust as needed

    # Test: Print config and loaded modules
    print("Enabled modules:", engine.config.enabled_modules)
    print("Scrip from config:", engine.config.get('scrip'))

    # Test end-to-end: Publish mock buy signal (as if from module 6)
    print("\nPublishing mock buy_signal...")
    engine.events.publish('buy_signal', {
        'quantity': 1,  # User-level (will * lot_size)
        'order_type': 'MARKET',
    })

    # Simulate order placed (get order_id from logs; manual for test)
    # Assume order_id = 'TEST123' (replace with real from logs if API responds)
    time.sleep(2)  # Wait for placement

    # Simulate WS update: Partial fill
    print("\nSimulating partial fill...")
    engine.events.publish('on_order_update', {
        'order_id': 'TEST123',  # Replace with actual from logs
        'status': 'PARTIAL',
        'filled_qty': 25,  # Half lot for test
        'price': 123.45,
        'fill_time': datetime.now()
    })

    # Simulate full fill
    print("\nSimulating full fill...")
    engine.events.publish('on_order_update', {
        'order_id': 'TEST123',
        'status': 'FILLED',
        'filled_qty': 25,  # Remaining to complete
        'price': 123.50,
        'fill_time': datetime.now()
    })

    # Check state after fill
    state_module = engine.modules.get('state')
    if state_module:
        print("\nState after buy fill: in_trade =", state_module.is_in_trade())
        print("Entry details:", state_module.get_entry_details())

    # Publish mock sell signal
    print("\nPublishing mock sell_signal...")
    engine.events.publish('sell_signal', {
        'quantity': 1,
        'order_type': 'MARKET',
    })

    # Simulate sell fill (similarly)
    time.sleep(2)
    engine.events.publish('on_order_update', {
        'order_id': 'TEST456',  # Mock sell order_id
        'status': 'FILLED',
        'filled_qty': 50,
        'price': 124.00,
        'fill_time': datetime.now()
    })

    # Check state after sell
    print("\nState after sell fill: in_trade =", state_module.is_in_trade())

    # Run loop (press Ctrl+C to stop)
    engine.run()  # Or while True: time.sleep(1) if run() already has loop
else:
    print("Engine start failed.")