from uuid import uuid4
from fastapi import APIRouter, HTTPException
from app.schemas.analysis import AnalyzeRequest
from app.ingestion.service import ingest_with_analysis
router=APIRouter(prefix='/analyses',tags=['analysis'])
@router.post('')
def create_analysis(payload:AnalyzeRequest):
 try:
  repo,sha,result,specialists,scoring,roadmap,report=ingest_with_analysis(str(payload.repository_url))
  return {'analysis_id':str(uuid4()),'status':'completed','repository':{'owner':repo.owner,'name':repo.repo,'url':repo.canonical_url,'commit_sha':sha},'analysis':result.model_dump(),'specialists':specialists.model_dump(),'assessment':scoring.model_dump(),'roadmap':roadmap.model_dump(),'report':report.model_dump()}
 except ValueError as e: raise HTTPException(422,detail=str(e))
 except Exception: raise HTTPException(502,detail='Repository ingestion or analysis failed safely')
