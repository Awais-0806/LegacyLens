import re
from pathlib import Path
from .base import Specialist
from .models import SpecialistResult
from ._util import f,ev
class SecuritySpecialist(Specialist):
 name='security'
 def analyze(self,a):
  out=[]
  if a.configuration.suspicious_files: out.append(f('security.suspicious-config',self.name,'indicator','Suspicious configuration filenames require review','Configuration filenames match static risk-oriented heuristics.',severity='low',confidence='low',evidence=[ev(x,'filename','Suspicious configuration indicator') for x in a.configuration.suspicious_files],impact='Configuration may contain security-sensitive behavior.',recommendation='Manually review without exposing values.',requires_manual_review=True,limitations=['Filename heuristic only.']))
  if not a.configuration.env_examples: out.append(f('security.no-env-example',self.name,'configuration','Environment example not detected','No .env.example-style file was detected.',severity='low',confidence='medium',impact='Required configuration may be undocumented or inconsistently provisioned.',recommendation='Provide a redacted environment template.'))
  if not a.documentation.categories.get('security',False): out.append(f('security.no-security-docs',self.name,'documentation','Security documentation indicator not detected','No security policy or security-focused documentation file was detected.',severity='low',confidence='medium',impact='Security reporting and handling expectations may be unclear.',recommendation='Add SECURITY.md or equivalent guidance.'))
  return SpecialistResult(findings=out)
