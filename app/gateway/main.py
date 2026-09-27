from __future__ import annotations
import os
import httpx
from fastapi import FastAPI, HTTPException
from app.common.models import JobRequest

COORDINATOR = os.getenv("COORDINATOR_URL", "http://coordinator:8000")
app = FastAPI(title="ThreadMesh API Gateway", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "role": "proxy"}


@app.post("/api/jobs")
async def submit(job: JobRequest) -> dict:
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(f"{COORDINATOR}/jobs", json=job.model_dump(mode="json"))
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Coordinator unavailable: {exc}") from exc
