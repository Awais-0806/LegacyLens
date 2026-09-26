from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

Category = Literal['architecture','security','dependencies','testing','documentation','maintainability','modernization_readiness']
Severity = Literal['info','low','medium','high','critical']
Confidence = Literal['low','medium','high']
Priority = Literal['P0','P1','P2','P3']
EvidenceStrength = Literal['verified','direct','inferred','heuristic','missing']

class CategoryScore(BaseModel):
    category: Category
    raw_score: float = Field(ge=0, le=100)
    weight: float = Field(ge=0, le=100)
    weighted_contribution: float = Field(ge=0, le=100)
    finding_count: int = Field(ge=0)
    high_or_critical_count: int = Field(ge=0)
    top_finding_ids: list[str] = Field(default_factory=list)
    positive_signals: list[str] = Field(default_factory=list)
    negative_signals: list[str] = Field(default_factory=list)
    explanation: str
    evidence_references: list[str] = Field(default_factory=list)
    confidence: Confidence = 'medium'
    limitations: list[str] = Field(default_factory=list)

class RiskPriority(BaseModel):
    risk_id: str
    priority: Priority
    category: Category
    title: str
    rationale: str
    severity: Severity
    confidence: Confidence
    impact: str
    evidence_references: list[str] = Field(default_factory=list)
    recommendation: str
    requires_manual_review: bool
    deterministic_or_inferred: Literal['deterministic','inferred']

class HealthAssessment(BaseModel):
    scoring_model_version: str
    overall_score: float = Field(ge=0, le=100)
    health_label: Literal['Excellent','Healthy','Needs Attention','At Risk','Critical Attention']
    risk_level: Literal['low','moderate','high','critical']
    category_scores: list[CategoryScore]
    weighted_score_breakdown: dict[str, float]
    risk_priorities: list[RiskPriority]
    positive_signals: list[str] = Field(default_factory=list)
    high_or_critical_findings: list[str] = Field(default_factory=list)
    executive_summary: str
    score_explanation: str
    confidence: Confidence
    limitations: list[str] = Field(default_factory=list)
    evidence_references: list[str] = Field(default_factory=list)

class ScoringResult(BaseModel):
    assessment: HealthAssessment
    processing_warnings: list[str] = Field(default_factory=list)
    scoring_status: Literal['completed','partial','failed'] = 'completed'
    deterministic: bool = True
