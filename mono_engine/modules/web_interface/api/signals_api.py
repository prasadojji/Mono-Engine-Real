"""
Signals API endpoint module.
Handles all signal-related data retrieval and processing.
"""

from flask import request, jsonify
from typing import Dict, Any, List
import pandas as pd

from ..core.db_utils import get_database_path, safe_sql_query
from ..core.data_utils import dataframe_to_json_serializable, safe_float
from ..core.response_utils import success_response, error_response, api_error_handler
from ..core.validation import validate_filter_params


@api_error_handler
def get_signals_data():
    """
    API endpoint to fetch signals data with filtering and pagination.

    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 50, max: 1000)
        symbol: Filter by symbol
        type: Filter by signal type (buy/sell)
        status: Filter by status
        from_date: Filter from date (YYYY-MM-DD)
        to_date: Filter to date (YYYY-MM-DD)

    Returns:
        JSON response with signals data
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
            'type': request.args.get('type'),
            'status': request.args.get('status'),
            'from_date': request.args.get('from_date'),
            'to_date': request.args.get('to_date'),
        }

        # Validate filters
        validated_filters = validate_filter_params(filters)

        # Build SQL query with filters
        query = """
            SELECT * FROM trades_signals
            WHERE 1=1
        """
        params = []

        if 'symbol' in validated_filters:
            query += " AND symbol = ?"
            params.append(validated_filters['symbol'])

        if 'type' in validated_filters:
            query += " AND signal_type = ?"
            params.append(validated_filters['type'])

        if 'status' in validated_filters:
            query += " AND status = ?"
            params.append(validated_filters['status'])

        if 'from_date' in validated_filters:
            query += " AND DATE(signal_time) >= ?"
            params.append(validated_filters['from_date'])

        if 'to_date' in validated_filters:
            query += " AND DATE(signal_time) <= ?"
            params.append(validated_filters['to_date'])

        # Add ordering and pagination
        query += " ORDER BY signal_time DESC"

        # Get total count for pagination
        count_query = f"SELECT COUNT(*) as total FROM ({query})"
        count_df = safe_sql_query(db_path, count_query, tuple(params))
        total_count = int(count_df.iloc[0]['total']) if not count_df.empty else 0

        # Add pagination to main query
        offset = (page - 1) * per_page
        query += " LIMIT ? OFFSET ?"
        params.extend([per_page, offset])

        # Execute main query
        signals_df = safe_sql_query(db_path, query, tuple(params))

        # Convert to JSON-serializable format
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
                # Log error but continue processing other signals
                print(f"Error processing signal row: {e}, row: {row}")
                continue

        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page

        response_data = {
            'signals': signals,
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
        print(f"Signals API Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(error_response("Failed to fetch signals data", "DATABASE_ERROR", str(e))), 500


@api_error_handler
def get_signals_stats():
    """
    API endpoint to get signals statistics.

    Returns:
        JSON response with signals statistics
    """
    try:
        db_path = get_database_path()

        # Get basic statistics
        stats_query = """
            SELECT
                COUNT(*) as total_signals,
                COUNT(CASE WHEN status = 'filled' THEN 1 END) as filled_signals,
                COUNT(CASE WHEN signal_type = 'buy' THEN 1 END) as buy_signals,
                COUNT(CASE WHEN signal_type = 'sell' THEN 1 END) as sell_signals,
                COUNT(CASE WHEN is_live = 1 THEN 1 END) as live_signals
            FROM trades_signals
        """

        stats_df = safe_sql_query(db_path, stats_query)

        if stats_df.empty:
            stats = {
                'total_signals': 0,
                'filled_signals': 0,
                'buy_signals': 0,
                'sell_signals': 0,
                'live_signals': 0
            }
        else:
            row = stats_df.iloc[0]
            stats = {
                'total_signals': int(row['total_signals']),
                'filled_signals': int(row['filled_signals']),
                'buy_signals': int(row['buy_signals']),
                'sell_signals': int(row['sell_signals']),
                'live_signals': int(row['live_signals'])
            }

        return jsonify(success_response({'stats': stats}))

    except Exception as e:
        print(f"Signals stats API Error: {e}")
        return jsonify(error_response("Failed to fetch signals statistics", "DATABASE_ERROR", str(e))), 500