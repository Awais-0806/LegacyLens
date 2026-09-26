from collections import defaultdict
from app.analysis.models import RepositoryAnalysis
from app.specialists.models import SpecialistReport, SpecialistFinding
from .models import *
from .weights import WEIGHTS

SEVERITY_DEDUCTION={'info':0.0,'low':3.0,'medium':8.0,'high':16.0,'critical':28.0}
CONF_FACTOR={'high':1.0,'medium':0.65,'low':0.3}
STRENGTH_FACTOR={'verified':1.0,'direct':1.0,'inferred':0.7,'heuristic':0.4,'missing':0.0}
PRIORITY_ORDER={'P0':0,'P1':1,'P2':2,'P3':3}
SEVERITY_ORDER={'critical':0,'high':1,'medium':2,'low':3,'info':4}

def _category(f):
    s=f.specialist.lower()
    return {'architecture':'architecture','security':'security','dependencies':'dependencies','testing':'testing','documentation':'documentation','maintainability':'maintainability','modernization':'modernization_readiness'}.get(s,'maintainability')

def _strength(f):
    if f.deterministic_or_inferred=='deterministic': return 'direct'
    return 'heuristic' if f.requires_manual_review else 'inferred'

def _risk_priority(f, strength):
    if f.severity=='critical' and f.confidence=='high' and strength in ('verified','direct'): return 'P0'
    if f.severity in ('critical','high'):
        return 'P1'
    if f.severity=='medium': return 'P2'
    return 'P3'

def _label(score):
    if score>=90:return 'Excellent'
    if score>=75:return 'Healthy'
    if score>=60:return 'Needs Attention'
    if score>=40:return 'At Risk'
    return 'Critical Attention'

def _risk_level(score, findings, risks):
    if any(f.severity=='critical' and f.confidence!='low' for f in findings): return 'critical'
    if any(r.priority in ('P0','P1') for r in risks) or score<40:return 'high'
    if score<75 or any(f.severity=='high' for f in findings):return 'moderate'
    return 'low'

def score_repository(analysis: RepositoryAnalysis, report: SpecialistReport) -> ScoringResult:
    grouped=defaultdict(list)
    for f in report.findings: grouped[_category(f)].append(f)
    cats=[]; risks=[]; all_evidence=[]; positives=[]
    for cat, weight in WEIGHTS.items():
        fs=grouped[cat]; deduction=0.0; neg=[]; refs=[]; high=0
        for f in fs:
            if f.severity in ('high','critical'): high+=1
            strength=_strength(f); factor=CONF_FACTOR[f.confidence]*STRENGTH_FACTOR[strength]
            deduction += SEVERITY_DEDUCTION[f.severity]*factor
            neg.append(f.title); refs.extend([e.path for e in f.evidence])
            if f.severity!='info': risks.append(RiskPriority(risk_id=f.finding_id,priority=_risk_priority(f,strength),category=cat,title=f.title,rationale=f.description,severity=f.severity,confidence=f.confidence,impact=f.impact,evidence_references=sorted(set([e.path for e in f.evidence])),recommendation=f.recommendation,requires_manual_review=f.requires_manual_review,deterministic_or_inferred=f.deterministic_or_inferred))
        # Explicit positive signals from deterministic evidence
        pos=[]
        if cat=='testing' and analysis.testing.test_files: pos.append('Test files detected')
        if cat=='dependencies' and analysis.dependency_summary.lockfiles: pos.append('Lockfile detected')
        if cat=='documentation' and analysis.documentation.has_readme: pos.append('README detected')
        if cat=='architecture' and analysis.entry_points: pos.append('Recognizable entry point detected')
        if cat=='modernization_readiness' and (analysis.configuration.ci_files or analysis.configuration.docker_files): pos.append('Automation or container configuration detected')
        if cat=='maintainability' and analysis.metrics.total_loc>0 and not analysis.metrics.deeply_nested_paths: pos.append('No deeply nested paths detected')
        if cat=='security' and analysis.configuration.env_examples: pos.append('Environment example configuration detected')
        score=max(0,min(100,100-deduction+min(8,len(pos)*2)))
        confidence='high' if fs and all(f.confidence=='high' for f in fs) else ('medium' if fs else 'low')
        cats.append(CategoryScore(category=cat,raw_score=round(score,2),weight=weight,weighted_contribution=round(score*weight/100,2),finding_count=len(fs),high_or_critical_count=high,top_finding_ids=[f.finding_id for f in sorted(fs,key=lambda x:(SEVERITY_ORDER[x.severity],x.finding_id))[:3]],positive_signals=pos,negative_signals=neg[:8],explanation=f'{len(fs)} specialist findings produced a bounded score from explicit severity, confidence, and evidence factors.',evidence_references=sorted(set(refs)),confidence=confidence,limitations=['Static analysis cannot confirm runtime behavior or exploitability.']))
        positives.extend(pos); all_evidence.extend(refs)
    risks=sorted({r.risk_id:r for r in risks}.values(),key=lambda r:(PRIORITY_ORDER[r.priority],SEVERITY_ORDER[r.severity],{'high':0,'medium':1,'low':2}[r.confidence],r.category,r.risk_id))
    overall=round(sum(c.weighted_contribution for c in cats),2)
    highcrit=sorted([f.finding_id for f in report.findings if f.severity in ('high','critical')])
    limitations=sorted(set(analysis.limitations+report.limitations+['Scores reflect detectable repository evidence; absence of evidence is not proof of absence.']))
    summary=f'Repository health is {overall:.2f}/100 ({_label(overall)}), with {len(risks)} prioritized engineering risks and {len(positives)} positive signals.'
    return ScoringResult(assessment=HealthAssessment(scoring_model_version='1.0.0',overall_score=overall,health_label=_label(overall),risk_level=_risk_level(overall,report.findings,risks),category_scores=cats,weighted_score_breakdown={c.category:c.weighted_contribution for c in cats},risk_priorities=risks,positive_signals=sorted(set(positives)),high_or_critical_findings=highcrit,executive_summary=summary,score_explanation='Each category starts at 100, applies bounded severity deductions adjusted by confidence and evidence strength, then adds small explicit positive-signal adjustments; category scores are weighted to 100.',confidence='high' if report.findings else 'medium',limitations=limitations,evidence_references=sorted(set(all_evidence))),processing_warnings=report.warnings,scoring_status='completed',deterministic=True)
