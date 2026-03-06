"""
Trades API endpoint module.
Handles all trade-related data retrieval and processing.
"""

from flask import request, jsonify
from typing import Dict, Any, List
import pandas as pd

from ..core.db_utils import get_database_path, safe_sql_query
from ..core.data_utils import safe_float, safe_int, safe_str, safe_datetime_str
from ..core.response_utils import success_response, error_response, api_error_handler
from ..core.validation import validate_filter_params


@api_error_handler
def get_trades_data():
    """
    API endpoint to fetch trades data with filtering and pagination.

    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 50, max: 1000)
        symbol: Filter by symbol
        pnl_filter: Filter by P&L (positive/negative)
        sell_reason: Filter by sell reason
        from_date: Filter from date (YYYY-MM-DD)
        to_date: Filter to date (YYYY-MM-DD)
        from_time: Filter from time (HH:MM)
        to_time: Filter to time (HH:MM)

    Returns:
        JSON response with trades data
    """
    try:
        # Get database path
        db_path = get_database_path()

        # Parse query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 1000)  # Max 1000 per page

        # Validate pagination
        if page < 1:
            return jsonify(error_response("Page must be >= 1", "INVALID_PAGE")), 400
        if per_page < 1:
            return jsonify(error_response("Per page must be >= 1", "INVALID_PER_PAGE")), 400

        # Get filter parameters
        filters = {
            'symbol': request.args.get('symbol'),
            'pnl_filter': request.args.get('pnl_filter'),
            'sell_reason': request.args.get('sell_reason'),
            'from_date': request.args.get('from_date'),
            'to_date': request.args.get('to_date'),
            'from_time': request.args.get('from_time'),
            'to_time': request.args.get('to_time'),
        }

        # Validate filters
        validated_filters = validate_filter_params(filters)

        # Build SQL query with filters
        query = """
            SELECT * FROM trades
            WHERE entry_time IS NOT NULL
            AND symbol NOT LIKE '%-51%'
        """
        params = []

        if 'symbol' in validated_filters:
            query += " AND symbol = ?"
            params.append(validated_filters['symbol'])

        if 'sell_reason' in validated_filters:
            query += " AND sell_reason = ?"
            params.append(validated_filters['sell_reason'])

        if 'from_date' in validated_filters:
            query += " AND DATE(entry_time) >= ?"
            params.append(validated_filters['from_date'])

        if 'to_date' in validated_filters:
            query += " AND DATE(entry_time) <= ?"
            params.append(validated_filters['to_date'])

        # Add ordering
        query += " ORDER BY entry_time DESC"

        # Get total count for pagination
        count_query = f"SELECT COUNT(*) as total FROM ({query})"
        count_df = safe_sql_query(db_path, count_query, tuple(params))
        total_count = int(count_df.iloc[0]['total']) if not count_df.empty else 0

        # Add pagination to main query
        offset = (page - 1) * per_page
        query += " LIMIT ? OFFSET ?"
        params.extend([per_page, offset])

        # Execute main query
        trades_df = safe_sql_query(db_path, query, tuple(params))

        # Apply P&L filter in Python (since it requires calculation)
        if 'pnl_filter' in validated_filters:
            pnl_filter = validated_filters['pnl_filter']
            filtered_trades = []

            for _, row in trades_df.iterrows():
                realized_pnl = safe_float(row.get('realized_pnl'))
                if pnl_filter == 'positive' and (realized_pnl is None or realized_pnl <= 0):
                    continue
                elif pnl_filter == 'negative' and (realized_pnl is None or realized_pnl > 0):
                    continue
                filtered_trades.append(row)

            trades_df = pd.DataFrame(filtered_trades) if filtered_trades else pd.DataFrame()

        # Convert to JSON-serializable format
        trades = []
        for _, row in trades_df.iterrows():
            try:
                # Safely convert entry_price (handle corrupted data)
                entry_price_raw = row.get('entry_price')
                if entry_price_raw in ['fixed_sl', 'strict_sl', 'profit_protect_10pct', 'immediate_sl'] or not pd.notna(entry_price_raw):
                    continue  # Skip corrupted trades

                entry_price = safe_float(entry_price_raw)
                if entry_price is None:
                    continue

                trade_data = {
                    'trade_id': safe_str(row.get('trade_id', '')),
                    'symbol': safe_str(row.get('symbol', '')),
                    'buy_reason': safe_str(row.get('buy_reason', '')),
                    'sell_reason': safe_str(row.get('sell_reason', 'unknown')),
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
                # Log error but continue processing other trades
                print(f"Error processing trade row: {e}, row: {row}")
                continue

        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page

        response_data = {
            'trades': trades,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            },
            'filters_applied': validated_filters
        }

        return jsonify(success_response(response_data))

    except Exception as e:
        print(f"Trades API Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(error_response("Failed to fetch trades data", "DATABASE_ERROR", str(e))), 500


@api_error_handler
def get_active_trades():
    """
    API endpoint to get currently active (open) trades.

    Returns:
        JSON response with active trades data
    """
    try:
        db_path = get_database_path()

        # Get active trades (no exit_time)
        query = """
            SELECT * FROM trades
            WHERE entry_time IS NOT NULL
            AND exit_time IS NULL
            AND symbol NOT LIKE '%-51%'
            ORDER BY entry_time DESC
        """

        trades_df = safe_sql_query(db_path, query)

        # Convert to JSON-serializable format
        active_trades = []
        for _, row in trades_df.iterrows():
            try:
                entry_price_raw = row.get('entry_price')
                if entry_price_raw in ['fixed_sl', 'strict_sl', 'profit_protect_10pct', 'immediate_sl'] or not pd.notna(entry_price_raw):
                    continue

                entry_price = safe_float(entry_price_raw)
                if entry_price is None:
                    continue

                trade_data = {
                    'trade_id': safe_str(row.get('trade_id', '')),
                    'symbol': safe_str(row.get('symbol', '')),
                    'buy_reason': safe_str(row.get('buy_reason', '')),
                    'entry_price': entry_price,
                    'quantity': safe_int(row.get('quantity'), 0),
                    'lot_size': safe_int(row.get('lot_size'), 1),
                    'entry_time': safe_datetime_str(row.get('entry_time')),
                    'is_historical': safe_int(row.get('is_historical'), 0),
                    'symbol_readable': safe_str(row.get('symbol_readable', ''))
                }
                active_trades.append(trade_data)
            except Exception as e:
                print(f"Error processing active trade row: {e}, row: {row}")
                continue

        return jsonify(success_response({'active_trades': active_trades}))

    except Exception as e:
        print(f"Active trades API Error: {e}")
        return jsonify(error_response("Failed to fetch active trades", "DATABASE_ERROR", str(e))), 500


@api_error_handler
def get_today_trades():
    """
    API endpoint to get today's trades.

    Returns:
        JSON response with today's trades data
    """
    try:
        from datetime import datetime

        db_path = get_database_path()
        today = datetime.now().strftime('%Y-%m-%d')

        # Get today's trades
        query = """
            SELECT * FROM trades
            WHERE entry_time IS NOT NULL
            AND DATE(entry_time) = ?
            AND symbol NOT LIKE '%-51%'
            ORDER BY entry_time DESC
        """

        trades_df = safe_sql_query(db_path, query, (today,))

        # Convert to JSON-serializable format
        today_trades = []
        for _, row in trades_df.iterrows():
            try:
                entry_price_raw = row.get('entry_price')
                if entry_price_raw in ['fixed_sl', 'strict_sl', 'profit_protect_10pct', 'immediate_sl'] or not pd.notna(entry_price_raw):
                    continue

                entry_price = safe_float(entry_price_raw)
                if entry_price is None:
                    continue

                trade_data = {
                    'trade_id': safe_str(row.get('trade_id', '')),
                    'symbol': safe_str(row.get('symbol', '')),
                    'buy_reason': safe_str(row.get('buy_reason', '')),
                    'sell_reason': safe_str(row.get('sell_reason', 'unknown')),
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
                today_trades.append(trade_data)
            except Exception as e:
                print(f"Error processing today's trade row: {e}, row: {row}")
                continue

        return jsonify(success_response({'today_trades': today_trades}))

    except Exception as e:
        print(f"Today's trades API Error: {e}")
        return jsonify(error_response("Failed to fetch today's trades", "DATABASE_ERROR", str(e))), 500


@api_error_handler
def get_trades_stats():
    """
    API endpoint to get trades statistics.

    Returns:
        JSON response with trades statistics
    """
    try:
        db_path = get_database_path()

        # Get comprehensive statistics
        stats_query = """
            SELECT
                COUNT(*) as total_trades,
                COUNT(CASE WHEN exit_time IS NOT NULL THEN 1 END) as completed_trades,
                COUNT(CASE WHEN exit_time IS NULL THEN 1 END) as active_trades,
                COUNT(CASE WHEN realized_pnl > 0 THEN 1 END) as profitable_trades,
                COUNT(CASE WHEN realized_pnl < 0 THEN 1 END) as losing_trades,
                SUM(CASE WHEN realized_pnl IS NOT NULL THEN realized_pnl ELSE 0 END) as total_pnl,
                AVG(CASE WHEN realized_pnl IS NOT NULL THEN realized_pnl ELSE NULL END) as avg_pnl,
                MAX(realized_pnl) as max_win,
                MIN(realized_pnl) as max_loss
            FROM trades
            WHERE entry_time IS NOT NULL
            AND symbol NOT LIKE '%-51%'
        """

        stats_df = safe_sql_query(db_path, stats_query)

        if stats_df.empty:
            stats = {
                'total_trades': 0,
                'completed_trades': 0,
                'active_trades': 0,
                'profitable_trades': 0,
                'losing_trades': 0,
                'total_pnl': 0,
                'avg_pnl': 0,
                'max_win': 0,
                'max_loss': 0,
                'win_rate': 0
            }
        else:
            row = stats_df.iloc[0]
            completed_trades = int(row['completed_trades']) if pd.notna(row['completed_trades']) else 0
            profitable_trades = int(row['profitable_trades']) if pd.notna(row['profitable_trades']) else 0

            stats = {
                'total_trades': int(row['total_trades']) if pd.notna(row['total_trades']) else 0,
                'completed_trades': completed_trades,
                'active_trades': int(row['active_trades']) if pd.notna(row['active_trades']) else 0,
                'profitable_trades': profitable_trades,
                'losing_trades': int(row['losing_trades']) if pd.notna(row['losing_trades']) else 0,
                'total_pnl': safe_float(row.get('total_pnl'), 0),
                'avg_pnl': safe_float(row.get('avg_pnl'), 0),
                'max_win': safe_float(row.get('max_win'), 0),
                'max_loss': safe_float(row.get('max_loss'), 0),
                'win_rate': (profitable_trades / completed_trades * 100) if completed_trades > 0 else 0
            }

        return jsonify(success_response({'stats': stats}))

    except Exception as e:
        print(f"Trades stats API Error: {e}")
        return jsonify(error_response("Failed to fetch trades statistics", "DATABASE_ERROR", str(e))), 500