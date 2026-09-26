from .base import Specialist
from .models import SpecialistResult
from ._util import f,ev
class DependencySpecialist(Specialist):
 name='dependencies'
 def analyze(self,a):
  d=a.dependency_summary; out=[]
  if d.manifest_files and not d.lockfiles: out.append(f('dependencies.no-lockfile',self.name,'reproducibility','Dependency lockfile not detected','Dependency manifests exist but no lockfile was detected.',severity='medium',confidence='high',evidence=[ev(x,'manifest','Dependency manifest') for x in d.manifest_files],impact='Builds may resolve different dependency versions.',recommendation='Commit the ecosystem-appropriate lockfile.'))
  if d.malformed_files: out.append(f('dependencies.malformed-manifest',self.name,'dependency-hygiene','Malformed dependency manifest detected','A dependency manifest could not be parsed safely.',severity='medium',confidence='high',evidence=[ev(x,'manifest','Malformed manifest') for x in d.malformed_files],impact='Automated dependency inventory may be incomplete.',recommendation='Repair the manifest and add validation in CI.'))
  return SpecialistResult(findings=out)
