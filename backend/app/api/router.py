from fastapi import APIRouter
from app.api.routes import health, analysis, ingestion, reports
api_router=APIRouter()
api_router.include_router(health.router)
api_router.include_router(analysis.router)
api_router.include_router(ingestion.router)
api_router.include_router(reports.router)
