import hashlib, html, json, re
from app.analysis.models import RepositoryAnalysis
from app.specialists.models import SpecialistReport
from app.scoring.models import ScoringResult
from app.roadmap.models import RoadmapResult
from .models import *

CATEGORY_ORDER=['architecture','security','dependencies','testing','documentation','maintainability','modernization_readiness']
def _safe_url(url:str)->str:
    return re.sub(r'[?#].*$', '', url)
def _refs(evidence): return sorted({f'{e.path}:{e.evidence_type}' for e in evidence})
def build_report(repo_url, repo_name, analysis:RepositoryAnalysis, specialists:SpecialistReport, scoring:ScoringResult, roadmap:RoadmapResult|None):
    a=scoring.assessment; rid='rpt-'+hashlib.sha256((repo_url+str(a.overall_score)+','.join(f.finding_id for f in specialists.findings)).encode()).hexdigest()[:16]
    action_map={x.action_id:x for x in (roadmap.roadmap.actions if roadmap else [])}
    finding_reports=[]
    for f in sorted(specialists.findings,key=lambda x:(x.category,x.severity,x.finding_id)):
        related=[aid for aid,x in action_map.items() if f.finding_id in x.source_finding_ids]
        finding_reports.append(FindingReport(finding_id=f.finding_id,specialist=f.specialist,category=f.category,title=f.title,severity=f.severity,confidence=f.confidence,description=f.description,impact=f.impact,recommendation=f.recommendation,evidence_references=_refs(f.evidence),source_classification=f.deterministic_or_inferred,requires_manual_review=f.requires_manual_review,remediation_action_ids=sorted(related),limitations=f.limitations))
    cats=[]
    for c in sorted(a.category_scores,key=lambda x:CATEGORY_ORDER.index(x.category) if x.category in CATEGORY_ORDER else 99):
        cats.append(CategoryReport(category=c.category,score=c.raw_score,weight=c.weight,weighted_contribution=c.weighted_contribution,explanation=c.explanation,strengths=c.positive_signals,concerns=c.negative_signals,finding_count=c.finding_count,evidence_references=sorted(c.evidence_references),limitations=c.limitations))
    concerns=[f.title for f in finding_reports if f.severity in ('high','critical')][:5]
    immediate=[r.title for r in sorted(a.risk_priorities,key=lambda x:(x.priority,x.risk_id))[:5]]
    executive=ExecutiveReport(title='LegacyLens Engineering Assessment',executive_summary=a.executive_summary,health_label=a.health_label,overall_score=a.overall_score,risk_level=a.risk_level,primary_concerns=concerns,key_strengths=a.positive_signals[:5],immediate_actions=immediate,modernization_outlook=(roadmap.roadmap.target_state if roadmap else 'A roadmap was not available from the current analysis.'),confidence=a.confidence,limitations=a.limitations)
    rr=None
    if roadmap:
        r=roadmap.roadmap; rr=RoadmapReport(summary=r.summary,current_state=r.current_state,target_state=r.target_state,quick_wins=r.quick_wins,phases=[x.model_dump() for x in r.roadmap_phases],prioritized_actions=[x.model_dump() for x in r.actions],blockers=[x.model_dump() for x in r.blockers],dependency_order=r.dependency_order,safety_warnings=r.safety_warnings,expected_benefits=r.expected_benefits)
    return AssessmentReport(metadata=ReportMetadata(report_id=rid,repository_url=_safe_url(repo_url),repository_identifier=repo_name,scoring_model_version=a.scoring_model_version,roadmap_version=roadmap.roadmap.roadmap_version if roadmap else 'unavailable'),executive=executive,category_reports=cats,findings=finding_reports,risks=[x.model_dump() for x in a.risk_priorities],roadmap=rr,positive_signals=a.positive_signals,limitations=sorted(set(a.limitations+(roadmap.roadmap.limitations if roadmap else []))),processing_warnings=sorted(set(specialists.warnings+(roadmap.processing_warnings if roadmap else []))),deterministic=True)
def to_json(report): return json.dumps(report.model_dump(),indent=2,sort_keys=True,ensure_ascii=False)
def to_markdown(r):
    lines=[f'# {r.executive.title}','',f'**Repository:** `{r.metadata.repository_identifier}`  ',f'**Health:** {r.executive.health_label} ({r.executive.overall_score:.1f}/100)  ',f'**Risk level:** {r.executive.risk_level}','', '## Executive Summary',r.executive.executive_summary,'','## Category Scores','| Category | Score | Weight | Contribution |','|---|---:|---:|---:|']
    lines += [f'| {c.category} | {c.score:.1f} | {c.weight:.1f}% | {c.weighted_contribution:.2f} |' for c in r.category_reports]
    lines += ['','## Strengths']+[f'- {x}' for x in r.executive.key_strengths] or lines
    lines += ['','## Primary Concerns']+[f'- {x}' for x in r.executive.primary_concerns]
    lines += ['','## Findings']
    for f in r.findings: lines += [f'### [{f.severity.upper()}] {f.title}',f'- ID: `{f.finding_id}`',f'- Specialist: {f.specialist}',f'- Confidence: {f.confidence}',f'- Description: {f.description}',f'- Recommendation: {f.recommendation}',f'- Manual review: {f.requires_manual_review}','']
    lines += ['## Risk Priorities']+[f'- **{x["priority"]}** {x["title"]} — {x["rationale"]}' for x in r.risks]
    if r.roadmap:
        lines += ['','## Renovation Roadmap',r.roadmap.summary,'','### Quick Wins']+[f'- `{x}`' for x in r.roadmap.quick_wins]
        lines += ['','### Phases']+[f'- **{p["sequence"]}. {p["name"]}** — {p["objective"]}' for p in r.roadmap.phases]
    lines += ['','## Limitations']+[f'- {x}' for x in r.limitations]
    return '\n'.join(lines)+'\n'
def to_html(r):
    md=to_markdown(r)
    body=''.join(f'<p>{html.escape(x)}</p>' for x in md.splitlines() if x and not x.startswith('|'))
    rows=''.join(f'<tr><td>{html.escape(c.category)}</td><td>{c.score:.1f}</td><td>{c.weight:.1f}%</td><td>{c.weighted_contribution:.2f}</td></tr>' for c in r.category_reports)
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LegacyLens Assessment</title><style>body{font-family:system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;line-height:1.5}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:.5rem;text-align:left}section{margin:1.5rem 0}.score{font-size:2rem;font-weight:700}</style></head><body><h1>LegacyLens Engineering Assessment</h1><div class="score">'+html.escape(f'{r.executive.overall_score:.1f}/100 — {r.executive.health_label}')+'</div><p>'+html.escape(r.executive.executive_summary)+'</p><section><h2>Category Scores</h2><table><thead><tr><th>Category</th><th>Score</th><th>Weight</th><th>Contribution</th></tr></thead><tbody>'+rows+'</tbody></table></section><section><h2>Detailed Report</h2>'+body+'</section></body></html>'
