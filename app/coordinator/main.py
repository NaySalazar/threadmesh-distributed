from __future__ import annotations
import os
from itertools import cycle
import httpx
from fastapi import FastAPI, HTTPException
from app.common.models import JobRequest

WORKERS = [w.strip() for w in os.getenv(
    "WORKER_ENDPOINTS",
    "http://worker-a:8000,http://worker-b:8000,http://worker-c:8000",
).split(",") if w.strip()]
_worker_cycle = cycle(WORKERS)
app = FastAPI(title="ThreadMesh Coordinator", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "workers": len(WORKERS)}


@app.post("/jobs")
async def dispatch(job: JobRequest) -> dict:
    errors: list[str] = []
    async with httpx.AsyncClient(timeout=6.0) as client:
        for _ in range(len(WORKERS)):
            endpoint = next(_worker_cycle)
            try:
                response = await client.post(f"{endpoint}/process", json=job.model_dump(mode="json"))
                response.raise_for_status()
                body = response.json()
                body["coordinator"] = "coordinator"
                return body
            except Exception as exc:
                errors.append(f"{endpoint}: {exc}")
    raise HTTPException(status_code=503, detail={"message": "No worker available", "errors": errors})
