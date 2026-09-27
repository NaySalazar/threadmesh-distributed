from __future__ import annotations
from typing import Optional

from app.worker.executor import WorkerExecutor


class LocalWorkerAdapter:
    """Test/simulation adapter for the WorkerPort."""

    def __init__(self, workers: dict[str, WorkerExecutor], failed_ids: Optional[set[str]] = None):
        self.workers = workers
        self.failed_ids = failed_ids or set()

    def execute(self, worker_id: str, payload: str, duration_ms: int) -> dict:
        if worker_id in self.failed_ids:
            raise ConnectionError(f"Worker {worker_id} unavailable")
        result = self.workers[worker_id].process(payload, duration_ms)
        return {
            "job_id": result.job_id,
            "worker_id": result.worker_id,
            "status": "completed",
            "elapsed_ms": round(result.elapsed_ms, 3),
            "result": result.value,
        }
