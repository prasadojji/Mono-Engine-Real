#!/usr/bin/env python3
import sys
import os
sys.path.append('mono_engine/modules')

from web_interface import get_signals_data
from flask import Flask

# Create a test Flask app context
app = Flask(__name__)
with app.app_context():
    try:
        result = get_signals_data()
        print("Function executed successfully")
        data = result.get_json()
        print(f"Total trades returned: {len(data['trades'])}")
        print(f"Total signals returned: {len(data['signals'])}")

        # Check for reconstructed trades
        reconstructed_trades = [t for t in data['trades'] if str(t.get('trade_id', '')).startswith('RECONSTRUCTED')]
        print(f"Reconstructed trades found: {len(reconstructed_trades)}")

        # Check March 4th trades
        march4_trades = [t for t in data['trades'] if t.get('entry_time', '').startswith('2026-03-04')]
        print(f"March 4th trades found: {len(march4_trades)}")

        if reconstructed_trades:
            print("Sample reconstructed trade:")
            print(reconstructed_trades[0])

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()