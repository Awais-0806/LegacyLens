from pathlib import Path
from .models import *
from .languages import detect_languages
from .frameworks import detect_technologies
from .dependencies import analyze_dependencies
from .testing import analyze_testing
from .documentation import analyze_documentation
from .configuration import analyze_configuration
from .metrics import analyze_metrics
IGNORED={'.git','node_modules','__pycache__','.venv','venv','dist','build','coverage','vendor','target','bin','obj'}
def analyze_repository(root:Path)->RepositoryAnalysis:
 files=[]; ignored=set()
 for p in root.rglob('*'):
  if any(part in IGNORED for part in p.parts): ignored.update(set(p.parts)&IGNORED); continue
  if p.is_file(): files.append(p)
 rel=lambda p:str(p.relative_to(root))
 data={'files':files,'rel':rel,'root':root}
 langs=detect_languages(data); tech=detect_technologies(data); deps=analyze_dependencies(data); tests=analyze_testing(data); docs=analyze_documentation(data); conf=analyze_configuration(data); metrics=analyze_metrics(data)
 findings=[]
 if not tests.test_files: findings.append(Finding(id='testing-no-tests',category='testing',title='No obvious tests detected',description='No test files were identified using static filename and path heuristics.',confidence='medium',limitations=['Static detection only; tests may exist under unconventional names.']))
 if not docs.has_readme: findings.append(Finding(id='docs-no-readme',category='documentation',title='README not detected',description='No README file was found at the analyzed repository level.',confidence='high'))
 return RepositoryAnalysis(file_count=len(files),directory_count=len({p.parent for p in files}),total_size_bytes=sum(p.stat().st_size for p in files),extensions=_ext(files),ignored_directories=sorted(ignored),languages=langs,technologies=tech,entry_points=_entries(files,root),dependency_summary=deps,testing=tests,documentation=docs,configuration=conf,metrics=metrics,findings=findings,limitations=['Static analysis only; repository code and dependencies were not executed.'])
def _ext(files):
 d={}
 for p in files: k=p.suffix.lower().lstrip('.') or '[no extension]'; d[k]=d.get(k,0)+1
 return d
def _entries(files,root):
 names={'main.py','app.py','manage.py','server.js','index.js','main.ts','main.go','main.rs','Program.cs','Application.java'}
 return [str(p.relative_to(root)) for p in files if p.name in names]
