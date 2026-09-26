from fastapi.testclient import TestClient
from app.main import app
from app.reports.models import AssessmentReport, ReportMetadata, ExecutiveReport

client = TestClient(app)

def sample():
    return AssessmentReport(
        metadata=ReportMetadata(report_id='rpt-test', repository_url='https://github.com/a/b', repository_identifier='a/b', scoring_model_version='1', roadmap_version='1'),
        executive=ExecutiveReport(title='Test', executive_summary='<script>alert(1)</script>', health_label='Healthy', overall_score=80, risk_level='low', modernization_outlook='Incremental', confidence='high'),
        category_reports=[], findings=[], risks=[], roadmap=None,
    ).model_dump()

def test_export_formats_have_safe_headers_and_content():
    body=sample()
    for fmt, content_type in [('json','application/json'),('markdown','text/markdown; charset=utf-8'),('html','text/html; charset=utf-8')]:
        r=client.post(f'/api/v1/reports/export/{fmt}', json=body)
        assert r.status_code == 200
        assert r.headers['content-type'].startswith(content_type.split(';')[0])
        assert 'attachment; filename="legacylens-assessment.' in r.headers['content-disposition']
    html=client.post('/api/v1/reports/export/html', json=body).text
    assert '<script>' not in html
    assert '&lt;script&gt;' in html
    assert 'https://' not in html.split('<style>',1)[-1]

def test_invalid_export_format_rejected():
    r=client.post('/api/v1/reports/export/xml', json=sample())
    assert r.status_code == 422
