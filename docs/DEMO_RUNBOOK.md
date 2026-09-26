# LegacyLens Demo Runbook

## Live demo path

### 1. Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Verify:

```bash
curl http://localhost:8000/api/v1/health
```

OpenAPI:

```text
http://localhost:8000/docs
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Set:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

### 3. Demo

1. Open the Next.js URL.
2. Paste a public HTTPS GitHub repository URL.
3. Start analysis.
4. Show the overview and health score.
5. Explain the score.
6. Filter and expand findings.
7. Show P0/P1 risks when present.
8. Walk through roadmap phases, actions, blockers, and manual-review warnings.
9. Download JSON, Markdown, and HTML.
10. Start another analysis.

## Deterministic backup

If outbound GitHub access is unavailable, do not pretend that a fixture result is a live GitHub run. Use the backend deterministic test/fixture workflow for a technical backup demonstration and narrate it as a local fixture validation.

## Current environment finding

In the validation environment used for this repository snapshot, `github.com` DNS resolution was unavailable. Therefore live GitHub analysis is currently environment-dependent even though the ingestion implementation and API path are present.

## Common failures

- **Frontend cannot install:** verify npm network access and run `npm install` on a normal networked machine.
- **Health database degraded:** check `APP_ENV`/database settings; local development should use SQLite fallback.
- **GitHub ingestion returns 502:** verify outbound DNS/network access and that the repository is public.
- **Export fails:** verify the analysis response contains a complete `report` object and that the backend export endpoint is reachable.
