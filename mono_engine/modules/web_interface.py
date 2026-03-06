"""
Simplified Web Interface for MoNo Engine Trading Dashboard.
Direct database connection without complex API layer.
"""

import sys
import os
import sqlite3
import json
from flask import Flask, render_template_string, jsonify

# Add the current directory to the path for imports when run as script
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from .ui.templates import get_main_template
except ImportError:
    # Fallback for when run as script
    from web_interface.ui.templates import get_main_template


def get_database_path():
    """Get the path to the database file."""
    # Look for database in current directory
    db_path = os.path.join(os.getcwd(), 'mono_engine_data.db')
    if os.path.exists(db_path):
        return db_path

    # Look in parent directory
    db_path = os.path.join(os.path.dirname(os.getcwd()), 'mono_engine_data.db')
    if os.path.exists(db_path):
        return db_path

    # Default fallback
    return 'mono_engine_data.db'


def get_signals_data():
    """Get signals and trades data directly from database."""
    try:
        db_path = get_database_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get signals
        cursor.execute("""
            SELECT * FROM trades_signals
            ORDER BY signal_time DESC
        """)
        signals_rows = cursor.fetchall()

        signals = []
        for row in signals_rows:
            signals.append({
                'signal_id': str(row['signal_id']),
                'symbol': str(row['symbol']),
                'signal_type': str(row['signal_type']),
                'signal_reason': str(row['signal_reason']),
                'signal_price': float(row['signal_price']) if row['signal_price'] else None,
                'candle_close': float(row['candle_close']) if row['candle_close'] else None,
                'signal_time': str(row['signal_time']),
                'fill_price': float(row['fill_price']) if row['fill_price'] else None,
                'fill_time': str(row['fill_time']) if row['fill_time'] else None,
                'realized_pnl': float(row['realized_pnl']) if row['realized_pnl'] else None,
                'is_live': int(row['is_live']) if row['is_live'] else 0,
                'status': str(row['status'])
            })

        # Get trades
        cursor.execute("""
            SELECT * FROM trades
            WHERE entry_time IS NOT NULL
            AND symbol NOT LIKE '%-51%'
            ORDER BY entry_time DESC
        """)
        trades_rows = cursor.fetchall()

        trades = []
        for row in trades_rows:
            # Skip corrupted rows
            entry_price = row['entry_price']
            if entry_price in ['fixed_sl', 'strict_sl', 'profit_protect_10pct', 'immediate_sl'] or not entry_price:
                continue

            try:
                entry_price = float(entry_price)
            except (ValueError, TypeError):
                continue

            trades.append({
                'trade_id': str(row['trade_id'] or ''),
                'symbol': str(row['symbol'] or ''),
                'buy_reason': str(row['buy_reason'] or ''),
                'sell_reason': str(row['sell_reason'] or 'unknown'),
                'entry_price': entry_price,
                'exit_price': float(row['exit_price']) if row['exit_price'] else None,
                'quantity': int(row['quantity']) if row['quantity'] else 0,
                'lot_size': int(row['lot_size']) if row['lot_size'] else 1,
                'entry_time': str(row['entry_time']) if row['entry_time'] else None,
                'exit_time': str(row['exit_time']) if row['exit_time'] else None,
                'realized_pnl': float(row['realized_pnl']) if row['realized_pnl'] else None,
                'is_historical': int(row['is_historical']) if row['is_historical'] else 0,
                'symbol_readable': str(row['symbol_readable'] or '')
            })

        conn.close()

        return {
            'signals': signals,
            'trades': trades
        }

    except Exception as e:
        print(f"Database error: {e}")
        return {
            'signals': [],
            'trades': []
        }


def create_app(config=None):
    """
    Create and configure the Flask application.

    Args:
        config: Optional configuration dictionary

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Apply configuration
    if config:
        app.config.update(config)

    # Simple API endpoint that returns data directly from database
    @app.route('/api/signals-data')
    def api_signals_data():
        """API endpoint that returns signals and trades data."""
        data = get_signals_data()
        return jsonify({
            'success': True,
            'data': data
        })

    # Register main dashboard route
    @app.route('/')
    @app.route('/dashboard')
    @app.route('/backtest-results')
    def dashboard():
        """Main dashboard route."""
        # Load data server-side
        data = get_signals_data()
        return render_template_string(get_main_template(data))

    return app


# For backward compatibility and direct execution
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000, host='0.0.0.0')
