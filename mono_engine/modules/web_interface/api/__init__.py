"""
API endpoints initialization module.
Registers all API endpoints with the Flask application.
"""

from .combined_api import get_signals_data
from .signals_api import get_signals_stats
from .trades_api import get_trades_data, get_active_trades, get_today_trades, get_trades_stats


def register_api_endpoints(app):
    """
    Register all API endpoints with the Flask application.

    Args:
        app: Flask application instance
    """
    # Main combined endpoint (backward compatibility)
    app.add_url_rule('/api/signals-data', 'get_signals_data', get_signals_data, methods=['GET'])

    # Signals endpoints
    app.add_url_rule('/api/signals/stats', 'get_signals_stats', get_signals_stats, methods=['GET'])

    # Trades endpoints
    app.add_url_rule('/api/trades', 'get_trades_data', get_trades_data, methods=['GET'])
    app.add_url_rule('/api/trades/active', 'get_active_trades', get_active_trades, methods=['GET'])
    app.add_url_rule('/api/trades/today', 'get_today_trades', get_today_trades, methods=['GET'])
    app.add_url_rule('/api/trades/stats', 'get_trades_stats', get_trades_stats, methods=['GET'])