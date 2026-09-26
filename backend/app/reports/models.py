from typing import Literal
from pydantic import BaseModel, Field

class ReportMetadata(BaseModel):
    report_id: str
    report_version: str = '1.0'
    repository_url: str
    repository_identifier: str
    analysis_status: str = 'completed'
    scoring_model_version: str
    roadmap_version: str

class ExecutiveReport(BaseModel):
    title: str
    executive_summary: str
    health_label: str
    overall_score: float = Field(ge=0, le=100)
    risk_level: str
    primary_concerns: list[str] = Field(default_factory=list)
    key_strengths: list[str] = Field(default_factory=list)
    immediate_actions: list[str] = Field(default_factory=list)
    modernization_outlook: str
    confidence: str
    limitations: list[str] = Field(default_factory=list)

class CategoryReport(BaseModel):
    category: str
    score: float
    weight: float
    weighted_contribution: float
    explanation: str
    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    finding_count: int = 0
    evidence_references: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

class FindingReport(BaseModel):
    finding_id: str
    specialist: str
    category: str
    title: str
    severity: str
    confidence: str
    description: str
    impact: str
    recommendation: str
    evidence_references: list[str] = Field(default_factory=list)
    source_classification: str
    requires_manual_review: bool
    remediation_action_ids: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

class RoadmapReport(BaseModel):
    summary: str
    current_state: str
    target_state: str
    quick_wins: list[str] = Field(default_factory=list)
    phases: list[dict] = Field(default_factory=list)
    prioritized_actions: list[dict] = Field(default_factory=list)
    blockers: list[dict] = Field(default_factory=list)
    dependency_order: list[str] = Field(default_factory=list)
    safety_warnings: list[str] = Field(default_factory=list)
    expected_benefits: list[str] = Field(default_factory=list)

class AssessmentReport(BaseModel):
    metadata: ReportMetadata
    executive: ExecutiveReport
    category_reports: list[CategoryReport]
    findings: list[FindingReport]
    risks: list[dict] = Field(default_factory=list)
    roadmap: RoadmapReport | None = None
    positive_signals: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    processing_warnings: list[str] = Field(default_factory=list)
    deterministic: bool = True
