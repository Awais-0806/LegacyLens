from app.analysis.models import RepositoryAnalysis
from .models import SpecialistReport,SpecialistExecution
from .architecture import ArchitectureSpecialist
from .security import SecuritySpecialist
from .dependencies import DependencySpecialist
from .testing import TestingSpecialist
from .documentation import DocumentationSpecialist
from .maintainability import MaintainabilitySpecialist
from .modernization import ModernizationSpecialist
SPECIALISTS=[ArchitectureSpecialist,SecuritySpecialist,DependencySpecialist,TestingSpecialist,DocumentationSpecialist,MaintainabilitySpecialist,ModernizationSpecialist]
def run_specialists(a:RepositoryAnalysis)->SpecialistReport:
 findings=[]; executions=[]; warnings=[]
 for cls in SPECIALISTS:
  name=cls.name
  try:
   r=cls().analyze(a); findings.extend(r.findings); executions.append(SpecialistExecution(specialist=name,status='completed',finding_count=len(r.findings)))
  except Exception as e:
   executions.append(SpecialistExecution(specialist=name,status='failed',error='specialist failed safely')); warnings.append(f'{name} specialist failed safely')
 findings.sort(key=lambda x:(x.specialist,x.finding_id))
 return SpecialistReport(findings=findings,executions=executions,warnings=warnings,limitations=['Specialist results are static evidence-based indicators; manual review remains required.'])
