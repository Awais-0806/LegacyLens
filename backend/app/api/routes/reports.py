from enum import Enum
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, Response
from app.reports.models import AssessmentReport
from app.reports.engine import to_json, to_markdown, to_html

router = APIRouter(prefix='/reports', tags=['reports'])

class ExportFormat(str, Enum):
    json = 'json'
    markdown = 'markdown'
    html = 'html'

@router.post('/export/{export_format}')
def export_report(export_format: ExportFormat, report: AssessmentReport):
    try:
        if export_format == ExportFormat.json:
            return Response(content=to_json(report), media_type='application/json', headers={'Content-Disposition': 'attachment; filename="legacylens-assessment.json"'})
        if export_format == ExportFormat.markdown:
            return PlainTextResponse(content=to_markdown(report), media_type='text/markdown', headers={'Content-Disposition': 'attachment; filename="legacylens-assessment.md"'})
        return Response(content=to_html(report), media_type='text/html', headers={'Content-Disposition': 'attachment; filename="legacylens-assessment.html"'})
    except Exception as exc:
        raise HTTPException(status_code=422, detail='Report export could not be generated safely') from exc
