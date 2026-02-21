# mono_engine/strategies/__init__.py
"""
Package for strategy classes and logic.
This file makes 'strategies' a proper Python package.
"""

# Expose key classes for easier imports from outside the package
from .base_strategy import BaseStrategy
from .afl_strategy import AFLStrategy
from .strategy import StrategyModule

# Optional: make relative imports more reliable (no need for __path__ assignment)
# The mere presence of this file + the above imports is enough