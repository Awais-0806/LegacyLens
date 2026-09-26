from .base import Specialist
from .models import SpecialistResult
from ._util import f,ev
class ModernizationSpecialist(Specialist):
 name='modernization'
 def analyze(self,a):
  out=[]; d=a.dependency_summary
  if d.manifest_files and not d.lockfiles: out.append(f('modernization.reproducible-deps',self.name,'modernization','Improve dependency reproducibility','Manifests exist without detected lockfiles.',severity='medium',confidence='high',recommendation='Add lockfiles before broad upgrades.',impact='Reproducibility can improve without changing application architecture.'))
  if not a.testing.test_files: out.append(f('modernization.characterization-tests',self.name,'modernization','Establish characterization tests','No obvious tests were detected.',severity='medium',confidence='medium',recommendation='Add focused characterization tests before refactoring.',impact='Creates a safety net for incremental change.'))
  if not a.documentation.has_readme: out.append(f('modernization.onboarding-docs',self.name,'modernization','Create onboarding documentation','README evidence was not detected.',severity='low',confidence='high',recommendation='Document setup, operation, and validation steps.',impact='Reduces onboarding friction.'))
  return SpecialistResult(findings=out)
