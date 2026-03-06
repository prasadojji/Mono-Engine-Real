import sqlite3
import pandas as pd
import json

# Connect to database and check the data
conn = sqlite3.connect('mono_engine_data.db')

# Get trades data
trades_df = pd.read_sql("""
    SELECT * FROM trades
    WHERE entry_time IS NOT NULL
    AND symbol NOT LIKE '%-51%'
    ORDER BY entry_time DESC
    LIMIT 5
""", conn)

print('Sample trade data:')
print(trades_df.head())
print()
print('Data types:')
print(trades_df.dtypes)
print()

# Try to process the data like in the web interface
trades = []
for _, row in trades_df.iterrows():
    try:
        # Handle the actual column structure from the database
        trade_symbol = row.get('symbol')
        exit_time = pd.to_datetime(row['exit_time']) if pd.notna(row['exit_time']) and row['exit_time'] else None

        # Skip corrupted rows entirely
        entry_price_raw = row.get('entry_price')
        if entry_price_raw in ['fixed_sl', 'strict_sl', 'profit_protect_10pct', 'immediate_sl'] or not pd.notna(entry_price_raw):
            print(f"Skipping corrupted trade {row.get('trade_id')} with invalid entry_price: {repr(entry_price_raw)}")
            continue

        try:
            entry_price = float(entry_price_raw)
        except (ValueError, TypeError):
            print(f"Warning: Could not convert entry_price '{entry_price_raw}' for trade {row.get('trade_id')}, skipping")
            continue

        # Safely convert all values to ensure JSON serializability
        def safe_float(value, default=None):
            try:
                if pd.notna(value) and value is not None and str(value).lower() not in ['nan', 'inf', '-inf']:
                    return float(value)
                return default
            except (ValueError, TypeError):
                return default

        def safe_int(value, default=0):
            try:
                if pd.notna(value) and value is not None and str(value).lower() not in ['nan', 'inf', '-inf']:
                    return int(value)
                return default
            except (ValueError, TypeError):
                return default

        trade_data = {
            'trade_id': str(row.get('trade_id', '')),
            'symbol': str(trade_symbol or ''),
            'buy_reason': str(row.get('buy_reason', '')),
            'entry_price': entry_price,  # Already validated as float above
            'exit_price': safe_float(row.get('exit_price')),
            'quantity': safe_int(row.get('quantity'), 0),
            'lot_size': safe_int(row.get('lot_size'), 1),
            'entry_time': str(row['entry_time']) if pd.notna(row.get('entry_time')) else None,
            'exit_time': str(row['exit_time']) if pd.notna(row.get('exit_time')) else None,
            'realized_pnl': safe_float(row.get('realized_pnl')),
            'is_historical': safe_int(row.get('is_historical'), 0),
            'sell_reason': str(row.get('sell_reason', 'unknown')),
            'symbol_readable': str(row.get('symbol_readable', ''))
        }

        print(f"Processing trade: {trade_data}")
        trades.append(trade_data)

    except Exception as e:
        print(f"Error processing trade row: {e}, row: {row}")
        continue

# Try to serialize to JSON
try:
    json_str = json.dumps({'trades': trades})
    print("JSON serialization successful!")
    print(f"JSON length: {len(json_str)}")
except Exception as e:
    print(f"JSON serialization failed: {e}")
    print(f"Trades data: {trades}")

conn.close()