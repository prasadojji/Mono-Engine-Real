"""
Modular Web Interface for MoNo Engine Trading Dashboard.

This module provides a clean, extensible web interface with proper separation of concerns:
- Core utilities for data processing, validation, and database operations
- Modular API endpoints for different data types
- UI templates and frontend assets
- Flask application factory for easy integration

Usage:
    from mono_engine.modules.web_interface.web_interface import create_app

    app = create_app()
    app.run(debug=True)
"""

__version__ = "2.0.0"
