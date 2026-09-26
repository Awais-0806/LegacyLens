from pathlib import Path
from .models import Manifest
EXT={'py':'Python','js':'JavaScript','ts':'TypeScript','tsx':'TypeScript','jsx':'JavaScript','java':'Java','go':'Go','rs':'Rust','rb':'Ruby','php':'PHP','cs':'C#','cpp':'C++','c':'C'}
def build_manifest(root:Path, max_files:int)->Manifest:
 files=[p for p in root.rglob('*') if p.is_file() and not any(x in {'.git','node_modules','__pycache__','.venv'} for x in p.parts)]
 if len(files)>max_files: raise ValueError('File count limit exceeded')
 dirs={p.parent for p in files}; ext={}; langs=set(); dep=[]; tests=[]; docs=[]; conf=[]; docker=[]; ci=[]; suspicious=[]; entries=[]
 for p in files:
  e=p.suffix.lower().lstrip('.'); ext[e]=ext.get(e,0)+1
  if e in EXT: langs.add(EXT[e])
  n=p.name.lower(); rel=str(p.relative_to(root))
  if n in {'package.json','requirements.txt','pyproject.toml','pom.xml','build.gradle','go.mod','cargo.toml','composer.json','gemfile'}: dep.append(rel)
  if 'test' in n or 'tests' in p.parts: tests.append(rel)
  if n.startswith('readme') or e in {'md','rst'}: docs.append(rel)
  if n in {'.env','docker-compose.yml','settings.py'} or 'config' in n: conf.append(rel)
  if 'dockerfile' in n: docker.append(rel)
  if '.github' in p.parts or 'jenkins' in n: ci.append(rel)
  if n in {'id_rsa','.pem','credentials.json','secrets.json'}: suspicious.append(rel)
  if n in {'main.py','app.py','manage.py','server.js','index.js','main.ts','main.go'}: entries.append(rel)
 return Manifest(file_count=len(files),directory_count=len(dirs),total_size_bytes=sum(p.stat().st_size for p in files),extensions=ext,languages=sorted(langs),entry_points=entries,dependency_manifests=dep,test_files=tests,documentation_files=docs,configuration_files=conf,docker_files=docker,ci_files=ci,suspicious_files=suspicious)
