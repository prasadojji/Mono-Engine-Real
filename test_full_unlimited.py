import sqlite3
import pandas as pd
import json

# Connect to database and check the full data without limits
conn = sqlite3.connect('mono_engine_data.db')

try:
    # Get signals from trades_signals table (no limit)
    signals_df = pd.read_sql("""
        SELECT * FROM trades_signals
        ORDER BY signal_time DESC
    """, conn)

    print(f'Signals count: {len(signals_df)}')

    # Convert to proper format like in web interface
    signals = []
    for _, row in signals_df.iterrows():
        try:
            signal_data = {
                'signal_id': row['signal_id'],
                'symbol': row['symbol'],
                'signal_type': row['signal_type'],
                'signal_reason': row['signal_reason'],
                'signal_price': float(row['signal_price']) if pd.notna(row['signal_price']) and row['signal_price'] else None,
                'candle_close': float(row['candle_close']) if pd.notna(row['candle_close']) and row['candle_close'] else None,
                'next_candle_direction': int(row['next_candle_direction']) if pd.notna(row['next_candle_direction']) and row['next_candle_direction'] else None,
                'signal_time': row['signal_time'],
                'fill_price': float(row['fill_price']) if pd.notna(row['fill_price']) and row['fill_price'] else None,
                'fill_time': row['fill_time'],
                'realized_pnl': float(row['realized_pnl']) if pd.notna(row['realized_pnl']) and row['realized_pnl'] else None,
                'is_live': int(row['is_live']) if pd.notna(row['is_live']) else 0,
                'status': row['status']
            }
            signals.append(signal_data)
        except Exception as e:
            print(f"Error processing signal row: {e}, row: {row}")
            continue

    # Get trades data (no limit)
    trades_df = pd.read_sql("""
        SELECT * FROM trades
        WHERE entry_time IS NOT NULL
        AND symbol NOT LIKE '%-51%'
        ORDER BY entry_time DESC
    """, conn)

    print(f'Trades count: {len(trades_df)}')

    # Process trades like in web interface
    trades = []
    for _, row in trades_df.iterrows():
        try:
            trade_symbol = row.get('symbol')
            exit_time = pd.to_datetime(row['exit_time']) if pd.notna(row['exit_time']) and row['exit_time'] else None

            entry_price_raw = row.get('entry_price')
            if entry_price_raw in ['fixed_sl', 'strict_sl', 'profit_protect_10pct', 'immediate_sl'] or not pd.notna(entry_price_raw):
                continue

            try:
                entry_price = float(entry_price_raw)
            except (ValueError, TypeError):
                continue

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
                'entry_price': entry_price,
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

            trades.append(trade_data)

        except Exception as e:
            print(f"Error processing trade row: {e}, row: {row}")
            continue

    print(f'Final counts - Signals: {len(signals)}, Trades: {len(trades)}')

    # Try to serialize to JSON
    try:
        result = {'signals': signals, 'trades': trades}
        json_str = json.dumps(result)
        print("JSON serialization successful!")
        print(f"JSON length: {len(json_str)}")

        # Check for any potential issues in the JSON
        lines = json_str.split('\n')
        if len(lines) >= 66:
            print(f"Line 66 content: {lines[65][:50]}...")
            if len(lines[65]) >= 20:
                print(f"Character at position 20 in line 66: '{lines[65][19]}'")

    except Exception as e:
        print(f"JSON serialization failed: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()

finally:
    conn.close()