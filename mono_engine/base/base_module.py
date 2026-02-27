# mono_engine/base/base_module.py
import logging

class BaseModule:
    def __init__(self, engine):
        self.engine = engine
        self.config = engine.config
        self.event_bus = engine.events
        self.logger = logging.getLogger(self.__class__.__name__)

    def start(self):
        """Override in subclasses if needed."""
        self.logger.info(f"Starting {self.__class__.__name__}")

    def stop(self):
        """Override in subclasses if needed."""
        self.logger.info(f"Stopping {self.__class__.__name__}")