# Canonical Report Export API

## Purpose

Report formatting is owned by the backend reporting engine. The frontend calls these endpoints instead of becoming a second authoritative report generator.

## Endpoints

```text
POST /api/v1/reports/export/json
POST /api/v1/reports/export/markdown
POST /api/v1/reports/export/html
```

Each endpoint accepts a validated `AssessmentReport` JSON body produced by the analysis pipeline.

## Response behavior

- JSON: `application/json`
- Markdown: `text/markdown`
- HTML: `text/html`
- All responses use fixed safe `Content-Disposition` filenames.
- No filesystem path is accepted from the client.
- Export errors use a safe public message without stack traces.

## Why request-scoped exports?

LegacyLens currently does not persist reports for later retrieval. Adding fake report records or an unnecessary persistence layer would obscure the actual architecture. The safe compromise is to accept the validated report object returned by an analysis request and serialize it using the same backend reporting engine.

## Security

Generated HTML is escaped through the reporting engine and uses an embedded minimal stylesheet only. It contains no scripts, CDNs, remote fonts, images, iframes, or tracking resources.

The endpoint does not evaluate repository content as instructions and does not execute report data.
