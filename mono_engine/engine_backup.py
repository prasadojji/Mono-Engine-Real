import logging
import importlib
import time

from mono_engine.config import Config
from mono_engine.core.events import EventDispatcher
from mono_engine.core.session import Session
from mono_engine.core.streamer import Streamer

class MonoEngine:
    def __init__(self, config_path: str = 'config.yaml'):
        self.config = Config.load(config_path)
        logging.basicConfig(level=getattr(logging, self.config.logging_level),
                            format='%(asctime)s - %(levelname)s - %(message)s')

        self.events = EventDispatcher()
        self.session = Session(self.config)
        self.streamer = Streamer(self.session, self.events)

        self.modules = []

    def _load_modules(self):
        for module_name in self.config.enabled_modules:
            try:
                module_path = f"mono_engine.modules.{module_name}"
                module = importlib.import_module(module_path)
                # Class name: title case, no underscore (e.g., market_data -> MarketData)
                class_name = module_name.replace("_", " ").title().replace(" ", "")
                if hasattr(module, class_name):
                    module_class = getattr(module, class_name)
                    module_instance = module_class(self)
                    self.modules.append(module_instance)
                    logging.info(f"Loaded module: {module_name} ({class_name})")
                else:
                    logging.error(f"Module {module_name} has no class {class_name}")
            except Exception as e:
                logging.error(f"Failed to load module {module_name}: {e}")

        for module in self.modules:
            try:
                module.start()
            except Exception as e:
                logging.error(f"Error starting module {module.__class__.__name__}: {e}")

    def login(self) -> bool:
        two_fa = input("\nEnter FRESH 6-digit 2FA code (generate now!): ").strip()
        if two_fa:
            self.session.config.credentials['two_fa'] = two_fa

        return self.session.login()

    def start(self) -> bool:
        if not self.login():
            logging.error("Engine start failed — login unsuccessful")
            return False

        logging.info("Engine authenticated — starting streamer")
        self.streamer.start()

        self._load_modules()
        logging.info(f"MonoEngine fully started — {len(self.modules)} modules loaded")
        return True

    def stop(self):
        logging.info("Stopping MonoEngine")
        for module in self.modules:
            try:
                module.stop()
            except Exception as e:
                logging.error(f"Error stopping module {module.__class__.__name__}: {e}")
        self.streamer.stop()
        self.session.close()

    def run(self):
        try:
            if self.start():
                logging.info("Engine running — press Ctrl+C to stop")
                while True:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.stop()