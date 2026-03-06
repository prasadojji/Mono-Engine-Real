"""
Combined API endpoint module.
Provides the main endpoint that returns both signals and trades data.
This maintains backward compatibility with the existing frontend.
"""

from flask import request, jsonify
from typing import Dict, Any, List
import pandas as pd

from ..core.db_utils import get_database_path, safe_sql_query
from ..core.data_utils import safe_float, safe_int, safe_str, safe_datetime_str
from ..core.response_utils import success_response, error_response, api_error_handler


@api_error_handler
def get_signals_data():
    """
    Main API endpoint that returns both signals and trades data.
    This maintains backward compatibility with the existing frontend.

    Returns:
        JSON response with signals and trades data
    """
    try:
        db_path = get_database_path()

        # Get signals from trades_signals table
        signals_query = """
            SELECT * FROM trades_signals
            ORDER BY signal_time DESC
        """
        signals_df = safe_sql_query(db_path, signals_query)

        # Convert signals to JSON-serializable format
        signals = []
        for _, row in signals_df.iterrows():
            try:
                signal_data = {
                    'signal_id': str(row['signal_id']),
                    'symbol': str(row['symbol']),
                    'signal_type': str(row['signal_type']),
                    'signal_reason': str(row['signal_reason']),
                    'signal_price': safe_float(row['signal_price']),
                    'candle_close': safe_float(row['candle_close']),
                    'next_candle_direction': safe_float(row['next_candle_direction']),
                    'signal_time': str(row['signal_time']),
                    'fill_price': safe_float(row['fill_price']),
                    'fill_time': str(row['fill_time']) if pd.notna(row.get('fill_time')) else None,
                    'realized_pnl': safe_float(row['realized_pnl']),
                    'is_live': int(row['is_live']) if pd.notna(row['is_live']) else 0,
                    'status': str(row['status'])
                }
                signals.append(signal_data)
            except Exception as e:
                print(f"Error processing signal row: {e}, row: {row}")
                continue

        # Get trades data with sell signal matching logic
        trades_df = safe_sql_query(db_path, """
            SELECT * FROM trades
            WHERE entry_time IS NOT NULL
            AND symbol NOT LIKE '%-51%'
            ORDER BY entry_time DESC
        """)

        # Get sell signals for matching
        sell_signals_df = safe_sql_query(db_path, """
            SELECT symbol, signal_reason, signal_time, status
            FROM trades_signals
            WHERE signal_type = 'sell' AND status = 'filled'
            ORDER BY signal_time DESC
        """)

        # Create lookup for sell signals by symbol and time proximity
        sell_signals_lookup = {}
        for _, signal_row in sell_signals_df.iterrows():
            symbol = signal_row['symbol']
            signal_time = pd.to_datetime(signal_row['signal_time'])
            signal_reason = signal_row['signal_reason']

            if symbol not in sell_signals_lookup:
                sell_signals_lookup[symbol] = []
            sell_signals_lookup[symbol].append({
                'time': signal_time,
                'reason': signal_reason
            })

        # Process trades with sell signal matching
        trades = []
        for _, row in trades_df.iterrows():
            try:
                trade_symbol = row.get('symbol')
                exit_time = pd.to_datetime(row['exit_time']) if pd.notna(row['exit_time']) and row['exit_time'] else None

                # Find matching sell reason from signals
                sell_reason = row.get('sell_reason', 'unknown')
                if sell_reason == 'unknown' and exit_time and trade_symbol in sell_signals_lookup:
                    # Find the closest signal within 5 minutes of exit time
                    closest_signal = None
                    min_time_diff = float('inf')

                    for signal in sell_signals_lookup[trade_symbol]:
                        time_diff = abs((exit_time - signal['time']).total_seconds())
                        if time_diff < min_time_diff and time_diff <= 300:  # 5 minutes
                            min_time_diff = time_diff
                            closest_signal = signal

                    if closest_signal:
                        sell_reason = closest_signal['reason']

                # Skip corrupted rows entirely
                entry_price_raw = row.get('entry_price')
                if entry_price_raw in ['fixed_sl', 'strict_sl', 'profit_protect_10pct', 'immediate_sl'] or not pd.notna(entry_price_raw):
                    continue  # Skip corrupted trades

                entry_price = safe_float(entry_price_raw)
                if entry_price is None:
                    continue

                trade_data = {
                    'trade_id': safe_str(row.get('trade_id', '')),
                    'symbol': safe_str(trade_symbol or ''),
                    'buy_reason': safe_str(row.get('buy_reason', '')),
                    'sell_reason': safe_str(sell_reason),
                    'entry_price': entry_price,
                    'exit_price': safe_float(row.get('exit_price')),
                    'quantity': safe_int(row.get('quantity'), 0),
                    'lot_size': safe_int(row.get('lot_size'), 1),
                    'entry_time': safe_datetime_str(row.get('entry_time')),
                    'exit_time': safe_datetime_str(row.get('exit_time')),
                    'realized_pnl': safe_float(row.get('realized_pnl')),
                    'is_historical': safe_int(row.get('is_historical'), 0),
                    'symbol_readable': safe_str(row.get('symbol_readable', ''))
                }
                trades.append(trade_data)
            except Exception as e:
                print(f"Error processing trade row: {e}, row: {row}")
                continue

        print(f"DEBUG: Returning {len(signals)} signals and {len(trades)} trades")
        return jsonify(success_response({
            'signals': signals,
            'trades': trades
        }))

    except Exception as e:
        print(f"Combined API Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(error_response("Failed to fetch data", "DATABASE_ERROR", str(e))), 500