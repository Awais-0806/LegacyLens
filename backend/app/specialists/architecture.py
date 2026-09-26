from .base import Specialist
from .models import SpecialistResult
from ._util import f,ev
class ArchitectureSpecialist(Specialist):
 name='architecture'
 def analyze(self,a):
  out=[]; files=max(a.file_count,1)
  if len(a.entry_points)>max(3,files//4): out.append(f('architecture.entrypoint-concentration',self.name,'structure','Entry points are concentrated','Multiple conventional entry points were detected, suggesting concentrated application startup surfaces.',severity='low',confidence='medium',evidence=[ev(x,'entry-point','Conventional entry point') for x in a.entry_points],impact='Changes may affect several startup paths.',recommendation='Map startup responsibilities before restructuring.',limitations=['Path-based static inference.']))
  if a.metrics.deeply_nested_paths: out.append(f('architecture.deep-nesting',self.name,'organization','Deep module nesting detected','Deeply nested paths may indicate unclear module boundaries.',severity='low',confidence='medium',evidence=[ev(x,'path','Deeply nested path') for x in a.metrics.deeply_nested_paths[:10]],impact='Navigation and ownership may become harder.',recommendation='Review boundaries and flatten only where responsibility is clear.'))
  if a.documentation.categories.get('architecture') is False: out.append(f('architecture.missing-docs',self.name,'documentation','Architecture documentation not detected','No architecture-specific documentation indicator was found.',severity='low',confidence='medium',evidence=[],impact='New contributors may lack system-level context.',recommendation='Add a concise architecture overview.',limitations=['Absence of detected files does not prove documentation is absent.']))
  return SpecialistResult(findings=out)
