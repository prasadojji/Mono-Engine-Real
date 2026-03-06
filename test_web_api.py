#!/usr/bin/env python3
import sys
import os
sys.path.append('.')

from mono_engine.modules.web_interface import app, get_signals_data
import json

def main():
    try:
        print("Testing API endpoint with Flask context...")
        with app.app_context():
            response = get_signals_data()
            if hasattr(response, 'get_json'):
                data = response.get_json()
            else:
                # Handle Response object
                data = json.loads(response.get_data(as_text=True))

            print(f"API working - Signals: {len(data.get('signals', []))}, Trades: {len(data.get('trades', []))}")
            if data.get('signals'):
                print("Sample signal keys:", list(data['signals'][0].keys()) if data['signals'] else 'No signals')
            if data.get('trades'):
                print("Sample trade keys:", list(data['trades'][0].keys()) if data['trades'] else 'No trades')
    except Exception as e:
        print(f"API Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
