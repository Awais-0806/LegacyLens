import json
from .models import DependencySummary
def analyze_dependencies(data):
 manifests=[]; locks=[]; malformed=[]; count=dev=0
 for p in data['files']:
  n=p.name.lower(); r=data['rel'](p)
  if n in {'package.json','requirements.txt','pyproject.toml','pom.xml','build.gradle','go.mod','cargo.toml','gemfile','composer.json','pipfile'}:
   manifests.append(r)
   if n=='package.json':
    try:
     x=json.loads(p.read_text(errors='ignore')); count+=len(x.get('dependencies',{})); dev+=len(x.get('devDependencies',{}))
    except Exception: malformed.append(r)
  if 'lock' in n or n in {'package-lock.json','pnpm-lock.yaml','yarn.lock','poetry.lock'}: locks.append(r)
 return DependencySummary(manifest_files=manifests,dependency_count=count,dev_dependency_count=dev,lockfiles=locks,malformed_files=malformed)
