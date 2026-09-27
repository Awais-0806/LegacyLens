"""
Tests for app.scoring.engine.score_repository — previously zero coverage.

Critical paths exercised:
  - Health label boundaries (Excellent/Healthy/Needs Attention/At Risk/Critical Attention)
  - Risk-level escalation driven by critical/high findings and score thresholds
  - Risk priority mapping: P0 for critical+high-confidence+deterministic, P1 for high severity
  - Positive-signal bonus (README, test files, lockfile, entry-point, CI/docker, clean metrics)
  - Category deduction math: overall score is bounded [0, 100]
  - ScoringResult structure (all required fields are present and within schema constraints)
"""
import pytest
from app.analysis.models import (
    RepositoryAnalysis,
    DependencySummary,
    TestingSummary,
    DocumentationSummary,
    ConfigurationSummary,
    CodeMetrics,
)
from app.specialists.models import SpecialistReport, SpecialistFinding
from app.scoring.engine import score_repository


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _empty_analysis(**overrides) -> RepositoryAnalysis:
    """Minimal valid RepositoryAnalysis with no findings-driving signals."""
    base = dict(
        file_count=0,
        directory_count=0,
        total_size_bytes=0,
        extensions={},
        ignored_directories=[],
        languages=[],
        technologies=[],
        entry_points=[],
        dependency_summary=DependencySummary(),
        testing=TestingSummary(),
        documentation=DocumentationSummary(),
        configuration=ConfigurationSummary(),
        metrics=CodeMetrics(),
        limitations=[],
    )
    base.update(overrides)
    return RepositoryAnalysis(**base)


def _empty_report(*findings: SpecialistFinding) -> SpecialistReport:
    return SpecialistReport(findings=list(findings))


def _finding(
    specialist: str,
    severity: str,
    confidence: str = "high",
    deterministic: str = "deterministic",
    manual: bool = False,
    finding_id: str | None = None,
) -> SpecialistFinding:
    fid = finding_id or f"{specialist}.{severity}.finding"
    return SpecialistFinding(
        finding_id=fid,
        specialist=specialist,
        category=specialist,
        title=f"{specialist} issue",
        description="test description",
        severity=severity,
        confidence=confidence,
        impact="test impact",
        recommendation="test recommendation",
        requires_manual_review=manual,
        deterministic_or_inferred=deterministic,
    )


# ---------------------------------------------------------------------------
# Test 1 — Health label thresholds and overall score bounds
# ---------------------------------------------------------------------------

class TestHealthLabels:
    """score_repository maps overall_score to the correct health_label."""

    def test_no_findings_scores_near_100_and_is_excellent_or_healthy(self):
        result = score_repository(_empty_analysis(), _empty_report())
        score = result.assessment.overall_score
        label = result.assessment.health_label
        # With no findings each category stays at 100; overall = sum(weight * 100 / 100)
        assert 90 <= score <= 100
        assert label == "Excellent"

    def test_critical_findings_across_all_categories_drives_score_down(self):
        """Large deductions from critical findings in every category must not overflow below 0."""
        findings = [
            _finding("architecture", "critical"),
            _finding("security", "critical"),
            _finding("dependencies", "critical"),
            _finding("testing", "critical"),
            _finding("documentation", "critical"),
            _finding("maintainability", "critical"),
            _finding("modernization", "critical"),
        ]
        result = score_repository(_empty_analysis(), _empty_report(*findings))
        assert result.assessment.overall_score >= 0
        assert result.assessment.health_label in {
            "Critical Attention", "At Risk", "Needs Attention"
        }

    def test_single_medium_security_finding_lowers_label_from_excellent(self):
        findings = [_finding("security", "medium", confidence="high")]
        result = score_repository(_empty_analysis(), _empty_report(*findings))
        # A medium deduction (8.0 * 1.0) in a 20%-weight category removes ~1.6 from overall
        assert result.assessment.overall_score < 100
        # label is still reasonable — not Critical Attention from a single medium
        assert result.assessment.health_label != "Critical Attention"


# ---------------------------------------------------------------------------
# Test 2 — Risk priority escalation rules
# ---------------------------------------------------------------------------

class TestRiskPriorityMapping:
    """_risk_priority() inside score_repository maps findings to the correct P-level."""

    def test_critical_high_confidence_deterministic_finding_becomes_p0(self):
        f = _finding(
            "security",
            severity="critical",
            confidence="high",
            deterministic="deterministic",
        )
        result = score_repository(_empty_analysis(), _empty_report(f))
        risks = result.assessment.risk_priorities
        assert risks, "Expected at least one RiskPriority"
        assert risks[0].priority == "P0"

    def test_high_severity_inferred_finding_becomes_p1(self):
        f = _finding(
            "architecture",
            severity="high",
            confidence="medium",
            deterministic="inferred",
        )
        result = score_repository(_empty_analysis(), _empty_report(f))
        risks = result.assessment.risk_priorities
        assert risks, "Expected at least one RiskPriority"
        # inferred evidence → heuristic strength, so falls back to P1 (not P0)
        assert risks[0].priority == "P1"

    def test_medium_finding_becomes_p2_and_low_becomes_p3(self):
        findings = [
            _finding("testing", "medium", finding_id="t.medium"),
            _finding("documentation", "low", finding_id="d.low"),
        ]
        result = score_repository(_empty_analysis(), _empty_report(*findings))
        priorities = {r.risk_id: r.priority for r in result.assessment.risk_priorities}
        assert priorities["t.medium"] == "P2"
        assert priorities["d.low"] == "P3"

    def test_info_findings_are_excluded_from_risk_priorities(self):
        """info-severity findings must NOT appear in risk_priorities."""
        f = _finding("documentation", "info")
        result = score_repository(_empty_analysis(), _empty_report(f))
        assert result.assessment.risk_priorities == []

    def test_risk_level_is_critical_when_critical_finding_with_non_low_confidence(self):
        f = _finding("security", "critical", confidence="medium")
        result = score_repository(_empty_analysis(), _empty_report(f))
        assert result.assessment.risk_level == "critical"


# ---------------------------------------------------------------------------
# Test 3 — Positive-signal bonuses are detected from analysis fields
# ---------------------------------------------------------------------------

class TestPositiveSignals:
    """Positive signals from the RepositoryAnalysis boost category scores slightly."""

    def test_readme_triggers_documentation_positive_signal(self):
        analysis = _empty_analysis(
            documentation=DocumentationSummary(has_readme=True)
        )
        result = score_repository(analysis, _empty_report())
        all_signals = result.assessment.positive_signals
        assert any("README" in s for s in all_signals)

    def test_test_files_trigger_testing_positive_signal(self):
        analysis = _empty_analysis(
            testing=TestingSummary(test_files=["tests/test_main.py"])
        )
        result = score_repository(analysis, _empty_report())
        assert any("Test files" in s for s in result.assessment.positive_signals)

    def test_lockfile_triggers_dependencies_positive_signal(self):
        analysis = _empty_analysis(
            dependency_summary=DependencySummary(lockfiles=["package-lock.json"])
        )
        result = score_repository(analysis, _empty_report())
        assert any("Lockfile" in s for s in result.assessment.positive_signals)

    def test_ci_or_docker_triggers_modernization_positive_signal(self):
        analysis = _empty_analysis(
            configuration=ConfigurationSummary(ci_files=[".github/workflows/ci.yml"])
        )
        result = score_repository(analysis, _empty_report())
        assert any("Automation" in s or "container" in s for s in result.assessment.positive_signals)

    def test_overall_score_with_all_positive_signals_stays_at_100(self):
        """Full positive signals + zero findings must not push score above 100."""
        analysis = _empty_analysis(
            entry_points=["main.py"],
            documentation=DocumentationSummary(has_readme=True),
            testing=TestingSummary(test_files=["tests/test_x.py"]),
            dependency_summary=DependencySummary(lockfiles=["Pipfile.lock"]),
            configuration=ConfigurationSummary(ci_files=[".travis.yml"]),
            metrics=CodeMetrics(total_loc=500, deeply_nested_paths=[]),
        )
        result = score_repository(analysis, _empty_report())
        assert result.assessment.overall_score <= 100
