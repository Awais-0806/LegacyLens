from enum import StrEnum
from pydantic import AnyHttpUrl, Field

from app.schemas.common import APIModel


class AnalysisStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


class AnalyzeRequest(APIModel):
    repository_url: AnyHttpUrl


class AnalyzeResponse(APIModel):
    analysis_id: str
    status: AnalysisStatus
    repository_url: str
    message: str = Field(min_length=1)
