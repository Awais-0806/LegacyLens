from dataclasses import dataclass
from app.core.config import get_settings
@dataclass(frozen=True)
class IngestionLimits:
 max_repository_size_mb:int=100; max_file_size_mb:int=10; max_file_count:int=10000; max_extraction_files:int=10000; timeout_seconds:int=30; max_total_extracted_size_mb:int=250; max_path_length:int=512

def get_limits():
 s=get_settings(); return IngestionLimits(s.max_repository_size_mb,s.max_file_size_mb,s.max_file_count,s.max_extraction_files,s.ingestion_timeout_seconds,s.max_total_extracted_size_mb,s.max_path_length)
