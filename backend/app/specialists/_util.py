from app.analysis.models import Evidence
from .models import SpecialistFinding
def ev(path,typ,detail): return Evidence(path=path,evidence_type=typ,detail=detail)
def f(id,sp,cat,title,desc,**kw): return SpecialistFinding(finding_id=id,specialist=sp,category=cat,title=title,description=desc,**kw)
