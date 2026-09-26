from .base import Specialist
from .models import SpecialistResult
from ._util import f,ev
class MaintainabilitySpecialist(Specialist):
 name='maintainability'
 def analyze(self,a):
  m=a.metrics; out=[]
  large=[x for x in m.largest_files if x.get('size_bytes',0)>50000]
  if large: out.append(f('maintainability.large-files',self.name,'complexity','Large source-file outliers detected',f'{len(large)} analyzed files exceed the static size threshold.',severity='medium',confidence='high',evidence=[ev(x.get('path',''),'metric','Large file size') for x in large],impact='Large modules may be harder to review and safely change.',recommendation='Characterize and decompose the largest modules incrementally.',limitations=['File size is not a complete complexity measure.']))
  if m.todo_count: out.append(f('maintainability.todo-concentration',self.name,'debt','TODO/FIXME markers detected',f'{m.todo_count} TODO/FIXME markers were detected.',severity='low',confidence='high',impact='Known unfinished work may accumulate.',recommendation='Triage markers into tracked issues.',evidence=[ev('repository','metric','TODO/FIXME count')]))
  return SpecialistResult(findings=out)
