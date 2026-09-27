from __future__ import annotations
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class LocalJobResult:
    job_id: str
    worker_id: str
    elapsed_ms: float
    value: str


class WorkerExecutor:
    """Executes independent jobs concurrently using a bounded thread pool."""

    def __init__(self, worker_id: str, max_threads: int = 4) -> None:
        self.worker_id = worker_id
        self._pool = ThreadPoolExecutor(max_workers=max_threads, thread_name_prefix=worker_id)

    def process(self, payload: str, duration_ms: int = 50) -> LocalJobResult:
        started = time.perf_counter()
        time.sleep(duration_ms / 1000.0)  # deterministic I/O-bound workload simulation
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
        elapsed = (time.perf_counter() - started) * 1000
        return LocalJobResult(str(uuid4()), self.worker_id, elapsed, digest)

    def submit(self, payload: str, duration_ms: int = 50):
        return self._pool.submit(self.process, payload, duration_ms)

    def close(self) -> None:
        self._pool.shutdown(wait=True, cancel_futures=False)
