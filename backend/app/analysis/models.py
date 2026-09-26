from pydantic import BaseModel, Field
from typing import Literal
class Evidence(BaseModel):
 path:str; evidence_type:str; detail:str
class Finding(BaseModel):
 id:str; category:str; title:str; description:str; evidence:list[Evidence]=[]; confidence:Literal['low','medium','high']='medium'; limitations:list[str]=[]
class LanguageSummary(BaseModel): language:str; file_count:int; loc:int; share:float; confidence:str; evidence_files:list[str]=[]
class Technology(BaseModel): technology:str; evidence:list[str]=[]; confidence:str
class DependencySummary(BaseModel): manifest_files:list[str]=[]; dependency_count:int=0; dev_dependency_count:int=0; lockfiles:list[str]=[]; malformed_files:list[str]=[]
class TestingSummary(BaseModel): test_files:list[str]=[]; frameworks:list[str]=[]; scripts:list[str]=[]; coverage_files:list[str]=[]; source_file_count:int=0; test_to_source_ratio:float=0
class DocumentationSummary(BaseModel): files:list[str]=[]; has_readme:bool=False; categories:dict[str,bool]={}
class ConfigurationSummary(BaseModel): files:list[str]=[]; docker_files:list[str]=[]; ci_files:list[str]=[]; env_examples:list[str]=[]; suspicious_files:list[str]=[]
class CodeMetrics(BaseModel): total_loc:int=0; average_file_size_bytes:float=0; largest_files:list[dict]=[]; todo_count:int=0; deeply_nested_paths:list[str]=[]
class RepositoryAnalysis(BaseModel): file_count:int; directory_count:int; total_size_bytes:int; extensions:dict[str,int]; ignored_directories:list[str]; languages:list[LanguageSummary]; technologies:list[Technology]; entry_points:list[str]; dependency_summary:DependencySummary; testing:TestingSummary; documentation:DocumentationSummary; configuration:ConfigurationSummary; metrics:CodeMetrics; findings:list[Finding]=[]; warnings:list[str]=[]; limitations:list[str]=[]
