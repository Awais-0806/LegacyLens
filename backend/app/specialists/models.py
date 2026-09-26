from pydantic import BaseModel, Field
from typing import Literal
from app.analysis.models import Evidence
Severity=Literal['info','low','medium','high','critical']
Confidence=Literal['low','medium','high']
class SpecialistFinding(BaseModel):
 finding_id:str; specialist:str; category:str; title:str; description:str
 severity:Severity='info'; confidence:Confidence='medium'; evidence:list[Evidence]=Field(default_factory=list)
 impact:str=''; recommendation:str=''; limitations:list[str]=Field(default_factory=list)
 requires_manual_review:bool=True; deterministic_or_inferred:Literal['deterministic','inferred']='inferred'
class SpecialistResult(BaseModel):
 findings:list[SpecialistFinding]=Field(default_factory=list); status:Literal['completed','failed']='completed'; error:str|None=None
class SpecialistExecution(BaseModel):
 specialist:str; status:Literal['completed','failed']; finding_count:int=0; error:str|None=None
class SpecialistReport(BaseModel):
 findings:list[SpecialistFinding]=Field(default_factory=list); executions:list[SpecialistExecution]=Field(default_factory=list); warnings:list[str]=Field(default_factory=list); limitations:list[str]=Field(default_factory=list)
