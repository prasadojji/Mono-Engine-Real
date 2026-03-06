"""
Modular Web Interface for MoNo Engine Trading Dashboard.
Provides a clean, extensible web interface with proper separation of concerns.
"""

import sys
import os

# Add the current directory to the path for imports when run as script
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from flask import Flask, render_template_string

try:
    from .api import register_api_endpoints
    from .ui.templates import get_main_template
except ImportError:
    # Fallback for when run as script
    from web_interface.api import register_api_endpoints
    from web_interface.ui.templates import get_main_template


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

    # Register API endpoints
    register_api_endpoints(app)

    # Register main dashboard route
    @app.route('/')
    @app.route('/dashboard')
    @app.route('/backtest-results')
    def dashboard():
        """Main dashboard route."""
        return render_template_string(get_main_template())

    return app


# For backward compatibility and direct execution
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000, host='0.0.0.0')