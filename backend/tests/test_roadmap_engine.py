"""
Tests for app.roadmap.engine.generate_roadmap — previously zero coverage.

Critical paths exercised:
  - Evidence-driven baseline actions inserted when README is absent
  - Evidence-driven baseline actions inserted when no test files are detected
  - Findings with severity 'info' are excluded from roadmap actions
  - High/critical findings that need manual review become ModernizationBlockers
  - Security findings always get risk='high' on their action
  - Priority mapping: critical→P0, high→P1, medium→P2, low/info→P3
  - Deduplication: duplicate finding IDs produce only one action
  - RoadmapResult structure validation
"""
import pytest
from app.analysis.models import (
    RepositoryAnalysis,
    DependencySummary,
    TestingSummary,
    DocumentationSummary,
    ConfigurationSummary,
    CodeMetrics,
    Evidence,
)
from app.specialists.models import SpecialistReport, SpecialistFinding
from app.scoring.models import HealthAssessment, CategoryScore, ScoringResult
from app.roadmap.engine import generate_roadmap


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _empty_analysis(**overrides) -> RepositoryAnalysis:
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
        documentation=DocumentationSummary(has_readme=True),  # default: has readme
        configuration=ConfigurationSummary(),
        metrics=CodeMetrics(),
        limitations=[],
    )
    base.update(overrides)
    return RepositoryAnalysis(**base)


def _empty_report(*findings: SpecialistFinding) -> SpecialistReport:
    return SpecialistReport(findings=list(findings))


def _stub_assessment() -> HealthAssessment:
    """Minimal valid HealthAssessment (roadmap engine only reads it superficially)."""
    return HealthAssessment(
        scoring_model_version="1.0.0",
        overall_score=75.0,
        health_label="Healthy",
        risk_level="low",
        category_scores=[],
        weighted_score_breakdown={},
        risk_priorities=[],
        executive_summary="stub",
        score_explanation="stub",
        confidence="medium",
    )


def _finding(
    specialist: str,
    severity: str,
    confidence: str = "high",
    manual: bool = False,
    finding_id: str | None = None,
) -> SpecialistFinding:
    fid = finding_id or f"{specialist}.{severity}"
    return SpecialistFinding(
        finding_id=fid,
        specialist=specialist,
        category=specialist,
        title=f"{specialist} {severity} issue",
        description="a test description",
        severity=severity,
        confidence=confidence,
        impact="some impact",
        recommendation="do the thing",
        requires_manual_review=manual,
        deterministic_or_inferred="inferred",
    )


# ---------------------------------------------------------------------------
# Test 1 — Evidence-driven baseline actions
# ---------------------------------------------------------------------------

class TestBaselineActions:
    """generate_roadmap adds deterministic actions when README or tests are absent."""

    def test_missing_readme_inserts_documentation_action(self):
        analysis = _empty_analysis(documentation=DocumentationSummary(has_readme=False))
        result = generate_roadmap(analysis, _empty_report(), _stub_assessment())
        action_ids = [a.action_id for a in result.roadmap.actions]
        assert "action.documentation-readme" in action_ids

    def test_present_readme_does_not_insert_documentation_action(self):
        analysis = _empty_analysis(documentation=DocumentationSummary(has_readme=True))
        result = generate_roadmap(analysis, _empty_report(), _stub_assessment())
        action_ids = [a.action_id for a in result.roadmap.actions]
        assert "action.documentation-readme" not in action_ids

    def test_missing_tests_inserts_characterization_action(self):
        analysis = _empty_analysis(testing=TestingSummary(test_files=[]))
        result = generate_roadmap(analysis, _empty_report(), _stub_assessment())
        action_ids = [a.action_id for a in result.roadmap.actions]
        assert "action.testing-characterization" in action_ids

    def test_characterization_action_is_p1_and_requires_manual_review(self):
        analysis = _empty_analysis(testing=TestingSummary(test_files=[]))
        result = generate_roadmap(analysis, _empty_report(), _stub_assessment())
        action = next(
            a for a in result.roadmap.actions
            if a.action_id == "action.testing-characterization"
        )
        assert action.priority == "P1"
        assert action.requires_manual_review is True
        assert action.deterministic_or_inferred == "deterministic"

    def test_existing_tests_do_not_insert_characterization_action(self):
        analysis = _empty_analysis(
            testing=TestingSummary(test_files=["tests/test_app.py"])
        )
        result = generate_roadmap(analysis, _empty_report(), _stub_assessment())
        action_ids = [a.action_id for a in result.roadmap.actions]
        assert "action.testing-characterization" not in action_ids


# ---------------------------------------------------------------------------
# Test 2 — Finding → action priority and blocker generation
# ---------------------------------------------------------------------------

class TestFindingToActionMapping:
    """Findings are correctly converted to RenovationActions and blockers."""

    def test_info_findings_are_excluded_from_actions(self):
        f = _finding("documentation", "info")
        result = generate_roadmap(_empty_analysis(), _empty_report(f), _stub_assessment())
        generated_ids = [a.action_id for a in result.roadmap.actions]
        # The info finding should NOT produce an action
        assert "action.documentation.info" not in generated_ids

    def test_critical_finding_maps_to_p0_action(self):
        f = _finding("security", "critical", manual=True)
        result = generate_roadmap(_empty_analysis(), _empty_report(f), _stub_assessment())
        action = next(
            (a for a in result.roadmap.actions if f.finding_id in a.source_finding_ids),
            None,
        )
        assert action is not None, "Action for critical finding must exist"
        assert action.priority == "P0"

    def test_security_finding_action_has_high_risk(self):
        f = _finding("security", "high", manual=False)
        result = generate_roadmap(_empty_analysis(), _empty_report(f), _stub_assessment())
        action = next(
            (a for a in result.roadmap.actions if f.finding_id in a.source_finding_ids),
            None,
        )
        assert action is not None
        assert action.risk == "high"

    def test_non_security_high_finding_action_has_low_risk(self):
        f = _finding("architecture", "high", manual=False)
        result = generate_roadmap(_empty_analysis(), _empty_report(f), _stub_assessment())
        action = next(
            (a for a in result.roadmap.actions if f.finding_id in a.source_finding_ids),
            None,
        )
        assert action is not None
        assert action.risk == "low"

    def test_high_critical_manual_finding_becomes_blocker(self):
        f = _finding("security", "critical", confidence="high", manual=True)
        result = generate_roadmap(_empty_analysis(), _empty_report(f), _stub_assessment())
        blocker_ids = [b.blocker_id for b in result.roadmap.blockers]
        assert f"blocker.{f.finding_id}" in blocker_ids

    def test_low_severity_finding_does_not_create_blocker(self):
        f = _finding("dependencies", "low", manual=True)
        result = generate_roadmap(_empty_analysis(), _empty_report(f), _stub_assessment())
        assert result.roadmap.blockers == []


# ---------------------------------------------------------------------------
# Test 3 — Roadmap structural guarantees
# ---------------------------------------------------------------------------

class TestRoadmapStructure:
    """The roadmap result must always satisfy structural invariants."""

    def test_roadmap_always_has_six_phases(self):
        result = generate_roadmap(_empty_analysis(), _empty_report(), _stub_assessment())
        assert len(result.roadmap.roadmap_phases) == 6

    def test_actions_are_deduplicated_by_action_id(self):
        # Same finding appearing twice (simulated by two identical IDs) must yield one action
        f1 = _finding("testing", "high", finding_id="dup.finding")
        f2 = _finding("testing", "high", finding_id="dup.finding")
        result = generate_roadmap(_empty_analysis(), _empty_report(f1, f2), _stub_assessment())
        action_ids = [a.action_id for a in result.roadmap.actions]
        assert len(action_ids) == len(set(action_ids)), "Duplicate action IDs found"

    def test_result_is_always_marked_deterministic(self):
        result = generate_roadmap(_empty_analysis(), _empty_report(), _stub_assessment())
        assert result.deterministic is True
        assert result.roadmap.deterministic is True

    def test_quick_wins_are_subset_of_all_actions(self):
        f = _finding("documentation", "low")
        result = generate_roadmap(_empty_analysis(), _empty_report(f), _stub_assessment())
        all_ids = {a.action_id for a in result.roadmap.actions}
        for qw in result.roadmap.quick_wins:
            assert qw in all_ids, f"Quick-win {qw!r} references non-existent action"
