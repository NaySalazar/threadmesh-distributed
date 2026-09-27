from __future__ import annotations
import os
from fastapi import FastAPI
from app.common.models import JobRequest, JobResult
from app.worker.executor import WorkerExecutor

WORKER_ID = os.getenv("WORKER_ID", "worker-local")
THREADS = int(os.getenv("THREADS", "4"))
executor = WorkerExecutor(WORKER_ID, THREADS)
app = FastAPI(title=f"ThreadMesh Worker {WORKER_ID}", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "worker_id": WORKER_ID, "threads": THREADS}


@app.post("/process", response_model=JobResult)
def process(job: JobRequest) -> JobResult:
    result = executor.process(job.payload, job.duration_ms)
    return JobResult(
        job_id=result.job_id,
        worker_id=result.worker_id,
        status="completed",
        elapsed_ms=round(result.elapsed_ms, 3),
        result=result.value,
    )
