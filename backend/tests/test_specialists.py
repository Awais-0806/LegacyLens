from pathlib import Path
from app.analysis.service import analyze_repository
from app.specialists.orchestrator import run_specialists
from app.specialists.models import SpecialistFinding

def fixture(name): return Path(__file__).parent/'fixtures'/name

def test_full_orchestrator_python():
 r=run_specialists(analyze_repository(fixture('python_project')))
 assert len(r.executions)==7 and all(x.status=='completed' for x in r.executions)
 assert r.findings==sorted(r.findings,key=lambda x:(x.specialist,x.finding_id))

def test_empty_repository():
 r=run_specialists(analyze_repository(fixture('empty_project')))
 assert r.findings and any(x.specialist=='testing' for x in r.findings)

def test_malformed_manifest_and_schema():
 a=analyze_repository(fixture('malformed_project')); r=run_specialists(a)
 assert a.dependency_summary.malformed_files
 assert all(isinstance(x, SpecialistFinding) for x in r.findings)
 assert all(x.severity in {'info','low','medium','high','critical'} for x in r.findings)

def test_typescript_fixture():
 r=run_specialists(analyze_repository(fixture('ts_project')))
 assert isinstance(r.findings,list)
