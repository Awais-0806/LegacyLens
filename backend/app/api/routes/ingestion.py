from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, AnyHttpUrl
from app.ingestion.service import ingest
from app.ingestion.fetcher import FetchError
from app.ingestion.archive import ArchiveSecurityError
router=APIRouter(prefix='/repositories',tags=['repositories'])
class IngestRequest(BaseModel): url: AnyHttpUrl
@router.post('/ingest')
def ingest_repository(payload:IngestRequest):
 try: return ingest(str(payload.url))
 except ValueError as e: raise HTTPException(422,str(e))
 except (FetchError,ArchiveSecurityError) as e: raise HTTPException(400,str(e))
 except Exception: raise HTTPException(500,'Repository ingestion failed safely')
