from __future__ import annotations
from dataclasses import dataclass
from itertools import cycle
from threading import Lock
from typing import Iterable, Optional


@dataclass(frozen=True)
class WorkerDescriptor:
    worker_id: str
    endpoint: str


class RoundRobinStrategy:
    """Strategy pattern: selects the next worker without coupling the coordinator to selection logic."""

    def __init__(self, workers: Iterable[WorkerDescriptor]):
        self._workers = list(workers)
        if not self._workers:
            raise ValueError("At least one worker is required")
        self._cycle = cycle(self._workers)
        self._lock = Lock()

    def next(self, healthy_ids: Optional[set[str]] = None) -> WorkerDescriptor:
        healthy_ids = healthy_ids or {w.worker_id for w in self._workers}
        if not healthy_ids:
            raise RuntimeError("No healthy workers available")
        with self._lock:
            for _ in range(len(self._workers)):
                candidate = next(self._cycle)
                if candidate.worker_id in healthy_ids:
                    return candidate
        raise RuntimeError("No healthy workers available")
