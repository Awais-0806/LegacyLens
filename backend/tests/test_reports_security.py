from fastapi.testclient import TestClient
from app.main import app
from app.reports.engine import to_html, to_json, to_markdown
from app.reports.models import AssessmentReport, ExecutiveReport, ReportMetadata

client = TestClient(app)


def report_with_content() -> AssessmentReport:
    return AssessmentReport(
        metadata=ReportMetadata(
            report_id="rpt-security",
            repository_url="https://github.com/example/demo?secret=ignored#fragment",
            repository_identifier="example/demo",
            scoring_model_version="1",
            roadmap_version="1",
        ),
        executive=ExecutiveReport(
            title="Test",
            executive_summary='<script>alert("x")</script> javascript: // </body>\nFAKE_API_KEY=not-a-real-secret',
            health_label="Healthy",
            overall_score=80,
            risk_level="low",
            modernization_outlook="Incremental",
            confidence="high",
        ),
        category_reports=[],
        findings=[],
        risks=[],
        roadmap=None,
    )


def test_report_serializers_are_deterministic_and_stable_for_empty_optional_sections():
    report = report_with_content()
    assert to_json(report) == to_json(report)
    assert to_markdown(report) == to_markdown(report)
    assert to_html(report) == to_html(report)
    assert report.roadmap is None


def test_html_export_is_escaped_and_self_contained():
    html = to_html(report_with_content())
    assert "<script>" not in html
    assert "</script>" not in html
    assert "&lt;script&gt;" in html
    assert "https://fonts" not in html
    assert "<link" not in html
    assert "<iframe" not in html
    assert "javascript:" in html  # repository-derived text is rendered as text, not navigated


def test_export_endpoint_rejects_invalid_report_shape_without_stacktrace():
    response = client.post("/api/v1/reports/export/json", json={"unexpected": True})
    assert response.status_code == 422
    assert "Traceback" not in response.text


def test_content_disposition_is_fixed_and_cannot_be_path_traversal_controlled():
    response = client.post("/api/v1/reports/export/json", json=report_with_content().model_dump())
    assert response.status_code == 200
    content_disposition = response.headers["content-disposition"]
    assert "../" not in content_disposition
    assert "\\" not in content_disposition
    assert "\r" not in content_disposition
    assert "\n" not in content_disposition
    assert content_disposition == 'attachment; filename="legacylens-assessment.json"'
