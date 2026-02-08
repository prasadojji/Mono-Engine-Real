from collections import defaultdict
from typing import Callable, Any, Dict, List


class EventDispatcher:
    """
    Simple, lightweight event dispatcher (pub/sub pattern).
    Used throughout MonoEngine for decoupled communication between modules.
    Thread-safe for basic use (callbacks called synchronously).
    """

    def __init__(self):
        self._callbacks: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """
        Subscribe a callback function to an event type.
        """
        if not callable(callback):
            raise ValueError("Callback must be callable")
        self._callbacks[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """
        Remove a specific callback from an event type.
        """
        if event_type in self._callbacks:
            self._callbacks[event_type] = [
                cb for cb in self._callbacks[event_type] if cb != callback
            ]

    def publish(self, event_type: str, data: Any = None) -> None:
        """
        Publish data to all callbacks subscribed to the event type.
        Callbacks are executed synchronously in subscription order.
        """
        callbacks = self._callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                # Log errors but don't break the chain
                print(f"Error in callback for event '{event_type}': {e}")

    def clear(self, event_type: str = None) -> None:
        """
        Clear all callbacks for a specific event or everything.
        """
        if event_type:
            self._callbacks[event_type].clear()
        else:
            self._callbacks.clear()


# Common event types (expand as needed)
EVENT_TICK = "on_tick"
EVENT_DEPTH = "on_depth"
EVENT_ORDER_UPDATE = "on_order_update"
EVENT_TRADE = "on_trade"
EVENT_GREEKS = "on_greeks"
EVENT_CONNECT = "on_connect"
EVENT_DISCONNECT = "on_disconnect"
EVENT_ERROR = "on_error" 
