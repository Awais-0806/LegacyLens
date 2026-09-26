const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export type Severity = "info" | "low" | "medium" | "high" | "critical";
export type Confidence = "low" | "medium" | "high";
export type Priority = "P0" | "P1" | "P2" | "P3";
export type Effort = "XS" | "S" | "M" | "L" | "XL";
export type AutomationSafety = "safe_to_automate" | "human_review_required" | "do_not_automate";
export type DeterministicOrInferred = "deterministic" | "inferred";

export interface EvidenceReference { path: string; evidence_type: string; detail: string; }
export interface LanguageSummary { language: string; file_count: number; loc: number; share: number; confidence: string; evidence_files: string[]; }
export interface Technology { technology: string; evidence: string[]; confidence: string; }
export interface DependencySummary { manifest_files: string[]; dependency_count: number; dev_dependency_count: number; lockfiles: string[]; malformed_files: string[]; }
export interface TestingSummary { test_files: string[]; frameworks: string[]; scripts: string[]; coverage_files: string[]; source_file_count: number; test_to_source_ratio: number; }
export interface DocumentationSummary { files: string[]; has_readme: boolean; categories: Record<string, boolean>; }
export interface ConfigurationSummary { files: string[]; docker_files: string[]; ci_files: string[]; env_examples: string[]; suspicious_files: string[]; }
export interface CodeMetrics { total_loc: number; average_file_size_bytes: number; largest_files: Record<string, unknown>[]; todo_count: number; deeply_nested_paths: string[]; }
export interface RepositoryFinding { id: string; category: string; title: string; description: string; evidence: EvidenceReference[]; confidence: Confidence; limitations: string[]; }
export interface RepositoryAnalysis {
  file_count: number; directory_count: number; total_size_bytes: number; extensions: Record<string, number>;
  ignored_directories: string[]; languages: LanguageSummary[]; technologies: Technology[]; entry_points: string[];
  dependency_summary: DependencySummary; testing: TestingSummary; documentation: DocumentationSummary;
  configuration: ConfigurationSummary; metrics: CodeMetrics; findings: RepositoryFinding[]; warnings: string[]; limitations: string[];
}

export interface SpecialistFinding {
  finding_id: string; specialist: string; category: string; title: string; description: string;
  severity: Severity; confidence: Confidence; evidence_references: string[]; impact: string;
  recommendation: string; limitations: string[]; requires_manual_review: boolean;
  source_classification: string;
}
export interface SpecialistExecution { specialist: string; status: "completed" | "failed"; finding_count: number; error: string | null; }
export interface SpecialistReport { findings: SpecialistFinding[]; executions: SpecialistExecution[]; warnings: string[]; limitations: string[]; }

export interface CategoryScore {
  category: string; raw_score: number; weight: number; weighted_contribution: number; finding_count: number;
  high_or_critical_count: number; top_finding_ids: string[]; positive_signals: string[]; negative_signals: string[];
  explanation: string; evidence_references: string[]; confidence: Confidence; limitations: string[];
}
export interface RiskPriority {
  risk_id: string; priority: Priority; category: string; title: string; rationale: string; severity: Severity;
  confidence: Confidence; impact: string; evidence_references: string[]; recommendation: string;
  requires_manual_review: boolean; deterministic_or_inferred: DeterministicOrInferred;
}
export interface HealthAssessment {
  scoring_model_version: string; overall_score: number; health_label: string; risk_level: string;
  category_scores: CategoryScore[]; weighted_score_breakdown: Record<string, number>; risk_priorities: RiskPriority[];
  positive_signals: string[]; high_or_critical_findings: string[]; executive_summary: string; score_explanation: string;
  confidence: Confidence; limitations: string[]; evidence_references: string[];
}
export interface ScoringResult { assessment: HealthAssessment; processing_warnings: string[]; scoring_status: "completed" | "partial" | "failed"; deterministic: boolean; }

export interface RenovationAction {
  action_id: string; title: string; description: string; category: string; priority: Priority; effort: Effort;
  impact: string; risk: string; phase: string; rationale: string; evidence_references: string[]; source_finding_ids: string[];
  prerequisites: string[]; expected_outcome: string; acceptance_criteria: string[]; requires_manual_review: boolean;
  automation_safety: AutomationSafety; deterministic_or_inferred: DeterministicOrInferred; limitations: string[];
}
export interface RoadmapPhase {
  phase_id: string; name: string; objective: string; sequence: number; action_ids: string[];
  entry_conditions: string[]; exit_conditions: string[]; blockers: string[]; expected_outcomes: string[]; manual_review_points: string[];
}
export interface ModernizationBlocker {
  blocker_id: string; title: string; description: string; category: string; severity: string; confidence: string;
  evidence_references: string[]; source_finding_ids: string[]; why_blocking: string; mitigation: string; requires_manual_review: boolean;
}
export interface RenovationRoadmap {
  roadmap_version: string; summary: string; current_state: string; target_state: string; recommended_sequence: string[];
  quick_wins: string[]; roadmap_phases: RoadmapPhase[]; actions: RenovationAction[]; blockers: ModernizationBlocker[];
  dependency_order: string[]; estimated_complexity: string; expected_benefits: string[]; safety_warnings: string[];
  limitations: string[]; evidence_references: string[]; deterministic: boolean;
}
export interface RoadmapResult { roadmap: RenovationRoadmap; roadmap_status: "completed" | "partial" | "failed"; processing_warnings: string[]; deterministic: boolean; }

export interface ReportMetadata {
  report_id: string; report_version: string; repository_url: string; repository_identifier: string;
  analysis_status: string; scoring_model_version: string; roadmap_version: string;
}
export interface ExecutiveReport {
  title: string; executive_summary: string; health_label: string; overall_score: number; risk_level: string;
  primary_concerns: string[]; key_strengths: string[]; immediate_actions: string[]; modernization_outlook: string;
  confidence: string; limitations: string[];
}
export interface CategoryReport {
  category: string; score: number; weight: number; weighted_contribution: number; explanation: string;
  strengths: string[]; concerns: string[]; finding_count: number; evidence_references: string[]; limitations: string[];
}
export interface FindingReport extends SpecialistFinding { remediation_action_ids: string[]; }
export interface RoadmapReport {
  summary: string; current_state: string; target_state: string; quick_wins: string[]; phases: RoadmapPhase[];
  prioritized_actions: RenovationAction[]; blockers: ModernizationBlocker[]; dependency_order: string[];
  safety_warnings: string[]; expected_benefits: string[];
}
export interface AssessmentReport {
  metadata: ReportMetadata; executive: ExecutiveReport; category_reports: CategoryReport[]; findings: FindingReport[];
  risks: RiskPriority[]; roadmap: RoadmapReport | null; positive_signals: string[]; limitations: string[];
  processing_warnings: string[]; deterministic: boolean;
}
export interface RepositoryMetadata { owner: string; name: string; url: string; commit_sha?: string | null; }
export interface AnalyzeResponse {
  analysis_id: string; status: string; repository: RepositoryMetadata; analysis: RepositoryAnalysis;
  specialists: SpecialistReport; assessment: ScoringResult; roadmap: RoadmapResult; report: AssessmentReport;
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { Accept: "application/json", "Content-Type": "application/json", ...(init?.headers ?? {}) },
    cache: "no-store",
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({} as { detail?: unknown; message?: unknown }));
    const detail = typeof body.detail === "string" ? body.detail : typeof body.message === "string" ? body.message : `Request failed (${response.status})`;
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export async function exportCanonicalReport(format: "json" | "markdown" | "html", report: AssessmentReport): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/reports/export/${format}`, {
    method: "POST",
    headers: { Accept: format === "html" ? "text/html" : format === "markdown" ? "text/markdown" : "application/json", "Content-Type": "application/json" },
    body: JSON.stringify(report),
    cache: "no-store",
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({} as { detail?: unknown }));
    throw new Error(typeof body.detail === "string" ? body.detail : "Report export could not be generated safely.");
  }
  return response.blob();
}
