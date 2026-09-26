from pydantic import BaseModel, Field
from typing import Literal
class RepositoryMetadata(BaseModel):
    owner:str; name:str; url:str; default_branch:str|None=None; commit_sha:str|None=None
class Manifest(BaseModel):
    file_count:int=0; directory_count:int=0; total_size_bytes:int=0; extensions:dict[str,int]={}; languages:list[str]=[]; entry_points:list[str]=[]; dependency_manifests:list[str]=[]; test_files:list[str]=[]; documentation_files:list[str]=[]; configuration_files:list[str]=[]; docker_files:list[str]=[]; ci_files:list[str]=[]; suspicious_files:list[str]=[]; ignored_directories:list[str]=[]
class IngestionResult(BaseModel):
    job_id:str; status:Literal['completed','failed','partial']; repository:RepositoryMetadata; manifest:Manifest; warnings:list[str]=[]
