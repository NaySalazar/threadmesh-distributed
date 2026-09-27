from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from app.coordinator.events import EventBus
from app.coordinator.strategy import RoundRobinStrategy, WorkerDescriptor


class WorkerPort(Protocol):
    def execute(self, worker_id: str, payload: str, duration_ms: int) -> dict: ...


@dataclass
class CoordinatorMediator:
    """Mediator pattern: centralizes communication and keeps clients/workers decoupled."""

    strategy: RoundRobinStrategy
    worker_port: WorkerPort
    events: EventBus

    def dispatch(self, payload: str, duration_ms: int, healthy_ids: set[str]) -> dict:
        attempted: set[str] = set()
        last_error: Exception | None = None
        while len(attempted) < len(healthy_ids):
            worker = self.strategy.next(healthy_ids - attempted)
            attempted.add(worker.worker_id)
            try:
                self.events.publish("job.dispatched", {"worker_id": worker.worker_id})
                result = self.worker_port.execute(worker.worker_id, payload, duration_ms)
                self.events.publish("job.completed", result)
                return result
            except Exception as exc:  # fallback to another healthy node
                last_error = exc
                self.events.publish("worker.failed", {"worker_id": worker.worker_id, "error": str(exc)})
        raise RuntimeError("All available workers failed") from last_error
