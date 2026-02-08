from abc import ABC, abstractmethod

class BaseModule(ABC):
    """
    Abstract base for all feature modules.
    Provides common interface and access to engine components.
    """

    def __init__(self, engine):
        self.engine = engine
        self.events = engine.events
        self.session = engine.session
        self.streamer = engine.streamer
        self.config = engine.config

    @abstractmethod
    def start(self):
        """Called when engine starts — subscribe to events, init state"""
        pass

    @abstractmethod
    def stop(self):
        """Called on engine stop — cleanup"""
        pass