import logging
from mono_engine.engine import MonoEngine
import time

# --- Add our imports here ---
# These are for the SENSEX logic (datetime for expiry, csv/io for parsing symbols, os for file checks)
from datetime import datetime
import csv
import io
import os

# Broker SDK for public symbols (to fetch Index/BSEOptions CSV if missing — no login needed)
from openapi_client import Configuration, ApiClient
from openapi_client.api import SymbolDetailsApi

# Import our new module (the sensex_options.py you created)
from mono_engine.modules.sensex_options import SensexOptions
from mono_engine.modules.order import Order  # For your test order

# ======================
# Your Original Code
# ======================
engine = MonoEngine()
engine.run()
time.sleep(5)  # Wait for streamer to connect (your original)

# ======================
# Load SensexOptions Module
# ======================
print("Loading Sensex Options Module...")
sensex_module = SensexOptions(engine)  # Create instance of the module, passing the engine
engine.modules.append(sensex_module)  # Add it to the engine's modules list
sensex_module.start()  # Call start() to run the grid, selection, live loop

# ======================
# Your Test AMO Order
# ======================
order_module = None
for mod in engine.modules:
    if isinstance(mod, Order):
        order_module = mod
        break
if order_module:
    order_module.place_order(
        symbol="RELIANCE_EQ_NSE",
        quantity=1,
        side="buy",
        order_type="limit",
        price=2800.0,
        amo=True,
        remarks="MonoEngine Test"
    )