from mono_engine.core.events import EventDispatcher, EVENT_TICK, EVENT_ORDER_UPDATE

# Create dispatcher
dispatcher = EventDispatcher()

# Test callback functions
def on_tick_handler(data):
    print("Tick event received:", data)

def on_order_handler(data):
    print("Order update event received:", data)

# Subscribe
dispatcher.subscribe(EVENT_TICK, on_tick_handler)
dispatcher.subscribe(EVENT_ORDER_UPDATE, on_order_handler)

# Publish test events
print("Publishing test events...\n")
dispatcher.publish(EVENT_TICK, {"symbol": "RELIANCE", "ltp": 2950.50})
dispatcher.publish(EVENT_ORDER_UPDATE, {"order_id": "12345", "status": "FILLED"})

# Test unsubscribe
dispatcher.unsubscribe(EVENT_TICK, on_tick_handler)
print("\nUnsubscribed from tick — publishing tick again (should not print handler)")
dispatcher.publish(EVENT_TICK, {"symbol": "TCS", "ltp": 4100.0})

# Test error in callback (won't break the system)
def bad_callback(data):
    raise ValueError("Simulated error in callback")

dispatcher.subscribe(EVENT_ORDER_UPDATE, bad_callback)
dispatcher.publish(EVENT_ORDER_UPDATE, {"order_id": "67890", "status": "REJECTED"})