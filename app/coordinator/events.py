from __future__ import annotations
from collections import defaultdict
from collections.abc import Callable
from threading import Lock


class EventBus:
    """Distributed Observer concept implemented locally for the prototype."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[dict], None]]] = defaultdict(list)
        self._lock = Lock()

    def subscribe(self, event_name: str, handler: Callable[[dict], None]) -> None:
        with self._lock:
            self._subscribers[event_name].append(handler)

    def publish(self, event_name: str, payload: dict) -> None:
        with self._lock:
            handlers = list(self._subscribers[event_name])
        for handler in handlers:
            handler(payload)
