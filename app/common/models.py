from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field


class JobType(str, Enum):
    IO = "io"
    CPU = "cpu"


class JobRequest(BaseModel):
    payload: str = Field(min_length=1, max_length=500)
    duration_ms: int = Field(default=50, ge=1, le=5000)
    job_type: JobType = JobType.IO


class JobResult(BaseModel):
    job_id: str
    worker_id: str
    status: str
    elapsed_ms: float
    result: str


class WorkerState(BaseModel):
    worker_id: str
    endpoint: str
    healthy: bool = True
