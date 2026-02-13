# mono_engine/engine.py
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

        self.modules = {}  # Changed to dict for keyed access
        self.mode = 'real'  # Default mode; set in run_engine.py after prompt

    def _load_modules(self):
        # Mapping for module_name to actual class name (adjust for your modules)
        class_map = {
            'portfolio': 'Portfolio',  # Assuming your existing portfolio.py class name
            'state': 'StateModule',    # For state.py
            'market_data': 'MarketData'    
            # Add others as needed; execution (order/paper) loaded conditionally
        }
        for module_name in self.config.enabled_modules:
            if module_name == 'order':  # Skip; handled conditionally
                continue
            try:
                module_path = f"mono_engine.modules.{module_name}"
                module = importlib.import_module(module_path)
                class_name = class_map.get(module_name)
                if class_name and hasattr(module, class_name):
                    module_class = getattr(module, class_name)
                    module_instance = module_class(self)
                    self.modules[module_name] = module_instance  # Use dict
                    logging.info(f"Loaded module: {module_name} ({class_name})")
                else:
                    logging.error(f"Module {module_name} has no class {class_name or 'unknown'}")
            except Exception as e:
                logging.error(f"Failed to load module {module_name}: {e}")

        # Conditionally load execution module based on mode
        if self.mode == 'paper':
            from mono_engine.modules.paper_trading import PaperTrading
            execution_class = PaperTrading
            execution_name = 'paper_trading'
        else:
            from mono_engine.modules.order import Order
            execution_class = Order
            execution_name = 'order'

        try:
            execution_instance = execution_class(self)
            self.modules['execution'] = execution_instance  # Unified key for access (e.g., in signals)
            logging.info(f"Loaded execution module: {execution_name} in {self.mode} mode")
        except Exception as e:
            logging.error(f"Failed to load execution module ({self.mode}): {e}")

        # Start modules (order matters if dependencies; e.g., state before execution)
        for module_name in ['state', 'execution']:  # Prioritize
            if module_name in self.modules:
                try:
                    self.modules[module_name].start()
                except Exception as e:
                    logging.error(f"Error starting module {module_name}: {e}")

        # Start remaining modules
        for module_name, module in self.modules.items():
            if module_name not in ['state', 'execution']:
                try:
                    module.start()
                except Exception as e:
                    logging.error(f"Error starting module {module_name}: {e}")

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
        logging.info(f"MonoEngine fully started — {len(self.modules)} modules loaded in {self.mode.upper()} mode")
        return True

    def stop(self):
        logging.info("Stopping MonoEngine")
        for module in self.modules.values():  # Updated to .values() for dict
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