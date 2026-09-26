from abc import ABC, abstractmethod
from app.analysis.models import RepositoryAnalysis
from .models import SpecialistResult
class Specialist(ABC):
 name='base'
 @abstractmethod
 def analyze(self, analysis:RepositoryAnalysis)->SpecialistResult: ...
