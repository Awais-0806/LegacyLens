from .models import Technology
def detect_technologies(data):
 names={p.name.lower():data['rel'](p) for p in data['files']}; out=[]
 def add(n,paths):
  if paths: out.append(Technology(technology=n,evidence=paths,confidence='high'))
 add('Docker',[v for k,v in names.items() if k=='dockerfile' or 'docker-compose' in k])
 add('GitHub Actions',[data['rel'](p) for p in data['files'] if '.github' in p.parts and 'workflows' in p.parts])
 if 'package.json' in names:
  p=next(p for p in data['files'] if p.name=='package.json')
  try:
   import json; x=json.loads(p.read_text(errors='ignore')); allv={**x.get('dependencies',{}),**x.get('devDependencies',{})}
   for key,label in [('next','Next.js'),('react','React'),('express','Express'),('vue','Vue'),('@angular/core','Angular')]:
    if key in allv: add(label,[data['rel'](p)])
  except Exception: pass
 for fn,label in [('requirements.txt','Python dependencies'),('pyproject.toml','Python project'),('pom.xml','Spring/Java build'),('go.mod','Go modules'),('Cargo.toml','Rust Cargo')]:
  if fn in names: add(label,[names[fn]])
 return out
