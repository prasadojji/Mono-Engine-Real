from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import pandas as pd


class BaseStrategy(ABC):
    """
    All strategies must inherit from this class.
    The engine will call these methods automatically.
    """
    def __init__(self, params: Dict[str, Any] = None):
        self.params = params or {}

    @abstractmethod
    def on_data_update(self, data: Dict[str, pd.DataFrame]):
        """
        Called every time new candle data arrives (1min, 5min, etc.)
        """
        pass

    @abstractmethod
    def should_enter(self) -> Tuple[bool, float | None]:
        """
        Return True + suggested entry price if we should buy now
        Otherwise return False, None
        """
        pass

    @abstractmethod
    def should_exit(self) -> Tuple[bool, float | None]:
        """
        Return True + suggested exit price if we should sell now
        Otherwise return False, None
        """
        pass

    def reset_day(self):
        """Optional: called at the start of a new trading day"""
        pass