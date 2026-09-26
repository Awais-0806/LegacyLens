from collections import defaultdict
from .models import *

def _action(f, phase, title, desc, effort='S', impact='medium', risk='low', prereq=None, safety='human_review_required'):
 cat=f.category; refs=sorted({e.path for e in f.evidence}); aid='action.'+f.finding_id.replace('.','-')
 return RenovationAction(action_id=aid,title=title,description=desc,category=cat,priority={'critical':'P0','high':'P1','medium':'P2','low':'P3','info':'P3'}[f.severity],effort=effort,impact=impact,risk=risk,phase=phase,rationale=f.description,evidence_references=refs,source_finding_ids=[f.finding_id],prerequisites=prereq or [],expected_outcome='A documented, reviewable improvement tied to the detected evidence.',acceptance_criteria=['Change is reviewed against the cited evidence','Existing behavior is validated before and after the change'],requires_manual_review=f.requires_manual_review,automation_safety=safety,deterministic_or_inferred='inferred',limitations=f.limitations or ['Static evidence does not establish runtime correctness.'])
def generate_roadmap(analysis, report, assessment):
 actions=[]; blockers=[]
 for f in report.findings:
  if f.severity=='info': continue
  title=f.recommendation or ('Review '+f.title)
  phase='stabilization' if f.severity in ('critical','high') else 'documentation_and_observability'
  effort='S' if f.severity in ('low','medium') else 'M'; impact='high' if f.severity in ('critical','high') else 'medium'; risk='high' if f.specialist=='security' else 'low'
  a=_action(f,phase,title,f'Remediate or review the evidence-backed issue: {f.title}.',effort,impact,risk)
  actions.append(a)
  if f.severity in ('critical','high') and (f.requires_manual_review or f.specialist=='security'):
   blockers.append(ModernizationBlocker(blocker_id='blocker.'+f.finding_id,title='Review required before major modernization',description=f.description,category=f.category,severity=f.severity,confidence=f.confidence,evidence_references=sorted({e.path for e in f.evidence}),source_finding_ids=[f.finding_id],why_blocking='The finding may create unacceptable uncertainty or blast radius during refactoring.',mitigation='Perform targeted manual review and record the decision before proceeding.',requires_manual_review=True))
 # evidence-driven baseline actions
 if not analysis.documentation.has_readme:
  actions.append(RenovationAction(action_id='action.documentation-readme',title='Add repository onboarding documentation',description='Create a README covering setup assumptions, entry points, and validation workflow.',category='documentation',priority='P2',effort='S',impact='medium',risk='low',phase='documentation_and_observability',rationale='No README was detected by deterministic analysis.',evidence_references=['README absence detected'],expected_outcome='New contributors can understand how to inspect and validate the repository.',acceptance_criteria=['README includes setup, entry points, and validation notes'],requires_manual_review=False,automation_safety='human_review_required',deterministic_or_inferred='deterministic'))
 if not analysis.testing.test_files:
  actions.append(RenovationAction(action_id='action.testing-characterization',title='Create characterization tests before risky refactoring',description='Establish a minimal regression baseline around detected application entry points.',category='testing',priority='P1',effort='M',impact='high',risk='medium',phase='stabilization',rationale='No obvious test files were detected.',evidence_references=['No obvious tests detected'],expected_outcome='Refactoring has a measurable regression safety net.',acceptance_criteria=['Baseline tests exist and are reviewed','Tests cover key entry-point behavior'],requires_manual_review=True,automation_safety='human_review_required',deterministic_or_inferred='deterministic'))
 actions=sorted({a.action_id:a for a in actions}.values(),key=lambda a:(a.priority,a.phase,a.action_id))
 ids={a.action_id for a in actions}; order=[]
 for a in actions:
  if a.action_id not in order: order.append(a.action_id)
 phases=[]
 for i,(pid,name,obj) in enumerate([('phase-0','Baseline and Safety','Preserve behavior and resolve review blockers'),('phase-1','Stabilization','Establish tests and address high-impact risks'),('phase-2','Documentation and Observability','Clarify architecture, setup, and maintainability signals'),('phase-3','Structural Refactoring','Introduce incremental boundaries only after safeguards'),('phase-4','Incremental Modernization','Modernize selectively with checkpoints'),('phase-5','Validation and Governance','Re-run assessment and institutionalize checks')]):
  aids=[a.action_id for a in actions if (a.phase=='stabilization' and i==1) or (a.phase=='documentation_and_observability' and i==2)]
  phases.append(RoadmapPhase(phase_id=pid,name=name,objective=obj,sequence=i,action_ids=aids,entry_conditions=['Use current assessment as baseline'],exit_conditions=['Review evidence and validate behavior'],blockers=[b.blocker_id for b in blockers if i<=1],expected_outcomes=[obj],manual_review_points=['Security and high-impact changes require human review']))
 current=f'Static assessment identified {len(report.findings)} specialist findings across the repository.'; target='A better-documented, testable, dependency-stable repository with incremental modernization boundaries and repeatable validation.'
 return RoadmapResult(roadmap=RenovationRoadmap(roadmap_version='1.0.0',summary=f'{len(actions)} evidence-backed modernization actions generated from the existing assessment.',current_state=current,target_state=target,recommended_sequence=[p.phase_id for p in phases],quick_wins=[a.action_id for a in actions if a.effort in ('XS','S') and a.risk=='low'],roadmap_phases=phases,actions=actions,blockers=blockers,dependency_order=order,estimated_complexity='moderate' if actions else 'low',expected_benefits=['Reduced modernization uncertainty','Improved regression safety','Clearer incremental engineering sequence'],safety_warnings=['Recommendations do not modify repository files automatically.','Static analysis cannot guarantee runtime correctness.'],limitations=sorted(set(analysis.limitations+report.limitations)),evidence_references=sorted({r for a in actions for r in a.evidence_references}),deterministic=True),processing_warnings=report.warnings)
