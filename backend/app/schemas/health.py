from pydantic import Field

from app.schemas.common import APIModel


class HealthResponse(APIModel):
    status: str = Field(pattern=r"^(ok|degraded)$")
    service: str
    version: str
    database: str
