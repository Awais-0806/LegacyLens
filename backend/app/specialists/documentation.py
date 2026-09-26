from .base import Specialist
from .models import SpecialistResult
from ._util import f,ev
class DocumentationSpecialist(Specialist):
 name='documentation'
 def analyze(self,a):
  d=a.documentation; out=[]
  if not d.has_readme: out.append(f('documentation.missing-readme',self.name,'onboarding','README not detected','No README file was detected.',severity='medium',confidence='high',impact='Initial setup and project purpose may be unclear.',recommendation='Add setup, usage, architecture, and validation instructions.'))
  missing=[k for k,v in d.categories.items() if not v]
  if missing: out.append(f('documentation.coverage-gaps',self.name,'onboarding','Documentation coverage gaps detected','Static indicators are missing for: '+', '.join(missing)+'.',severity='low',confidence='medium',impact='Operational knowledge may remain implicit.',recommendation='Document the highest-impact missing areas.',limitations=['File indicators do not assess document quality.']))
  return SpecialistResult(findings=out)
