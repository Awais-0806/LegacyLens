from .base import Specialist
from .models import SpecialistResult
from ._util import f,ev
class TestingSpecialist(Specialist):
 name='testing'
 def analyze(self,a):
  t=a.testing; out=[]
  if not t.test_files: out.append(f('testing.no-obvious-tests',self.name,'coverage','No obvious tests detected','No test files were identified by static heuristics.',severity='medium',confidence='medium',impact='Refactoring may be riskier without regression protection.',recommendation='Create characterization tests before major modernization.',limitations=['Tests may use unconventional names.']))
  elif t.test_to_source_ratio < .1 and t.source_file_count>0: out.append(f('testing.low-test-density',self.name,'coverage','Low test-to-source file ratio','Detected test files are sparse relative to source files.',severity='low',confidence='medium',evidence=[ev(x,'test-file','Detected test file') for x in t.test_files[:10]],impact='Important behavior may have limited visible regression protection.',recommendation='Prioritize tests around critical and high-change modules.'))
  return SpecialistResult(findings=out)
