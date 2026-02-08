import logging
from mono_engine.engine import MonoEngine

engine = MonoEngine()
engine.run()

import time
# Wait for connection
time.sleep(5)

# Find Order module and place safe AMO test order
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
        price=2800.0,      # Safe low price (won't fill)
        amo=True,          # After Market Order — queues for tomorrow
        remarks="MonoEngine Test"
    )