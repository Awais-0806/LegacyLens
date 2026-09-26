from pathlib import Path
from app.analysis.service import analyze_repository
ROOT=Path(__file__).parent/'fixtures'
def test_python_analysis():
 r=analyze_repository(ROOT/'python_project'); assert any(x.language=='Python' for x in r.languages)
def test_empty_analysis():
 r=analyze_repository(ROOT/'empty_project'); assert r.file_count==0
def test_typescript_framework():
 r=analyze_repository(ROOT/'ts_project'); assert any(x.technology=='React' for x in r.technologies)
def test_malformed_dependency():
 r=analyze_repository(ROOT/'malformed_project'); assert r.dependency_summary.malformed_files
