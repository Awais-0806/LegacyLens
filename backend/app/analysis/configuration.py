from .models import ConfigurationSummary
def analyze_configuration(data):
 files=[]; docker=[]; ci=[]; env=[]; suspicious=[]
 for p in data['files']:
  n=p.name.lower(); r=data['rel'](p)
  if n in {'.env.example','pyproject.toml','settings.py','config.yaml','config.yml'} or 'config' in n: files.append(r)
  if n=='dockerfile' or 'docker-compose' in n: docker.append(r)
  if '.github' in p.parts or n in {'jenkinsfile','.gitlab-ci.yml'}: ci.append(r)
  if n=='.env.example': env.append(r)
  if n in {'credentials.json','secrets.json','id_rsa'}: suspicious.append(r)
 return ConfigurationSummary(files=files,docker_files=docker,ci_files=ci,env_examples=env,suspicious_files=suspicious)
