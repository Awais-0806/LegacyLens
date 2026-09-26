# LegacyLens

**Understand legacy code. See the risks. Modernize with confidence.**

LegacyLens is a security-conscious developer intelligence platform that turns a **public GitHub repository** into an evidence-backed modernization assessment. It focuses on deterministic static analysis, specialist review, conservative health scoring, prioritized risks, and a human-review-aware renovation roadmap.

## What problem does it solve?

Before changing an old repository, engineers often spend significant time answering basic questions: What is here? How is it structured? Where are the risky or fragile areas? What evidence supports those concerns? What should be changed first?

LegacyLens turns that initial investigation into a repeatable assessment workflow without executing repository code or silently inventing runtime facts.

## Product flow

**DISCOVER → UNDERSTAND → PRIORITIZE → MODERNIZE**

1. Submit a public GitHub repository URL.
2. Safely ingest the repository into a temporary workspace.
3. Detect languages, technologies, dependencies, testing/documentation signals, configuration, and code metrics.
4. Run seven deterministic specialist analyzers.
5. Calculate a weighted health assessment and risk priorities.
6. Generate an evidence-backed renovation roadmap.
7. Present the result in an interactive Next.js dashboard.
8. Export the canonical engineering report as JSON, Markdown, or standalone HTML.

## Core features

- Public GitHub URL validation with server-side authority.
- Bounded archive ingestion with traversal/link/resource protections.
- No repository code execution and no dependency installation during analysis.
- Deterministic repository analysis.
- Seven specialist analyzers: Architecture, Security, Dependencies, Testing, Documentation, Maintainability, and Modernization Readiness.
- Weighted health scoring with controlled severity/confidence/evidence effects.
- P0–P3 risk prioritization.
- Evidence-linked renovation actions, quick wins, blockers, prerequisites, and acceptance criteria.
- Explainability-first assessment dashboard.
- Canonical backend JSON, Markdown, and HTML exports.
- Responsive frontend with accessible labels, filters, expandable findings, and safe export downloads.

## Seven specialist analyzers

| Specialist | Focus |
|---|---|
| Architecture | Entry-point concentration, structural signals, architecture documentation gaps |
| Security | Conservative configuration/security indicators and documentation gaps |
| Dependencies | Lockfiles, manifests, malformed dependency metadata, reproducibility signals |
| Testing | Test discovery, framework/script signals, test density, coverage evidence |
| Documentation | README presence and documentation category gaps |
| Maintainability | Large-file outliers and TODO/FIXME debt markers |
| Modernization Readiness | Safe modernization prerequisites such as characterization tests, documentation, and reproducible dependencies |

Findings distinguish evidence from inference. A heuristic indicator is not presented as a confirmed vulnerability.

## Health scoring

The current scoring model uses these category weights:

| Category | Weight |
|---|---:|
| Architecture | 15% |
| Security | 20% |
| Dependencies | 15% |
| Testing | 15% |
| Documentation | 10% |
| Maintainability | 15% |
| Modernization Readiness | 10% |

Scores are bounded to 0–100 and combine controlled severity, confidence, evidence-strength, and positive-signal adjustments. The UI uses the resulting backend assessment; it does not invent or recalculate the score.

## Architecture

```text
┌──────────────────────┐
│   Next.js Frontend   │
│ Assessment Dashboard │
└──────────┬───────────┘
           │ POST /api/v1/analyses
           │ POST /api/v1/reports/export/*
           ▼
┌──────────────────────┐
│      FastAPI API     │
├──────────────────────┤
│ URL Validation       │
│ Safe Ingestion       │
│ Deterministic        │
│ Analysis             │
├──────────────────────┤
│ 7 Specialist Engine  │
├──────────────────────┤
│ Health / Risk Score  │
├──────────────────────┤
│ Renovation Roadmap   │
├──────────────────────┤
│ Canonical Reporting  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Temporary Repository │
│ Workspace            │
│ No Code Execution    │
└──────────────────────┘
```

## Technology stack

Backend:
- Python 3.13-compatible environment
- FastAPI
- Pydantic / pydantic-settings
- SQLAlchemy
- SQLite for local/test fallback; PostgreSQL target for non-development environments
- HTTPX
- pytest

Frontend:
- Next.js 15
- React 19
- TypeScript 5
- Tailwind CSS 3

No queue, microservice layer, authentication system, or cloud infrastructure is required by the current design.

## Security model

LegacyLens is intentionally conservative:

- Only HTTPS `github.com/<owner>/<repo>` repository URLs are accepted.
- Credentials, custom ports, query strings, and fragments are rejected by the repository URL validator.
- GitHub archive redirects are rejected.
- Archive extraction has path, file-count, per-file, total-size, and path-length limits.
- ZIP/TAR symlink and hardlink protections are applied.
- Temporary repository workspaces are cleaned up after analysis.
- Repository code is not executed.
- Dependencies are not installed from the inspected repository.
- API request sizes and endpoint/IP request rates are bounded.
- Security headers and restricted CORS are enabled.
- Errors returned to clients do not expose internal stack traces.
- Generated HTML is escaped and contains no external scripts, fonts, images, tracking, or CDN resources.

These controls are security-conscious safeguards, not a guarantee that a repository is vulnerability-free.

## Local setup

### 1. Backend

```bash
cd backend
python -m venv .venv
# activate the virtual environment
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/api/v1/health
```

### 2. Frontend

Create the frontend environment if needed:

```bash
cd frontend
```

Set the API base URL:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

Install and run:

```bash
npm install
npm run dev
```

The frontend dependency installation/build was not reproducible in the constrained validation environment used for this repository snapshot because npm network access timed out. Run the commands above on a normal networked development machine before the live demo.

## Environment variables

See `.env.example`. Important settings include:

- `APP_ENV`
- `DATABASE_URL`
- `SQLITE_DATABASE_URL`
- `CORS_ORIGINS`
- repository and archive safety limits
- request-size and rate-limit settings

Do not place backend secrets in `NEXT_PUBLIC_*` variables.

## API endpoints

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/health` | Runtime/database health |
| `POST /api/v1/analyses` | Canonical repository analysis pipeline |
| `POST /api/v1/repositories/ingest` | Safe repository ingestion surface |
| `POST /api/v1/reports/export/json` | Canonical JSON report export |
| `POST /api/v1/reports/export/markdown` | Canonical Markdown report export |
| `POST /api/v1/reports/export/html` | Canonical standalone HTML report export |
| `/docs` | FastAPI OpenAPI documentation |

Reports are request-scoped in the current architecture; there is no fake persistent report store. Canonical export endpoints therefore accept the validated report object returned by the analysis pipeline.

## Testing

Backend regression suite:

```bash
cd backend
pytest -q
```

Python compilation:

```bash
cd ..
python -m compileall -q backend/app
```

Frontend validation on a normal networked development machine:

```bash
cd frontend
npm ci   # when a lockfile is present
# or npm install
npm run lint
npx tsc --noEmit
npm run build
```

## Demo workflow

1. Start the backend and verify `/api/v1/health`.
2. Start the Next.js frontend.
3. Paste a public GitHub repository URL.
4. Run the assessment.
5. Show the health score and explainability panel.
6. Open specialist findings and P0/P1 risks.
7. Walk through quick wins, blockers, prerequisites, and roadmap phases.
8. Download JSON, Markdown, and HTML reports.

Live GitHub ingestion requires outbound DNS/network access. When network access is unavailable, use the deterministic local backend fixtures/tests documented in `docs/DEMO_RUNBOOK.md`; do not present fixture results as fresh live GitHub analysis.

## IBM Bob development workflow

IBM Bob was used as the development/workflow environment for iterative planning, implementation, verification, debugging, documentation, and phase-by-phase hardening. The product itself does **not** claim an IBM Bob runtime API, SDK, or runtime integration.

The development process used a phased workflow: inspect → implement → test → document → review → harden. See `docs/BOB_WORKFLOW.md` for the project-specific record.

## Current validation status

Implemented and locally verified:
- backend application and regression suite
- Python compilation
- health route and OpenAPI registration
- canonical report export endpoints
- export security behavior

Environment-dependent / currently unverified in this constrained workspace:
- frontend npm dependency installation
- frontend lint/typecheck/build
- browser-level QA
- live GitHub ingestion
- authentic screenshot/video capture

## Known limitations

- Analysis is static; it does not perform runtime application security testing.
- Findings are conservative indicators and may require manual review.
- No automatic source-code rewriting is performed.
- Live GitHub ingestion requires network access.
- The current frontend does not expose true backend progress telemetry.
- Reports are not persisted for later retrieval in the current architecture.
- In-process rate limiting is designed for local/sandbox use rather than horizontally scaled production.

## Team

- Awais Jabbar
- Muhammad Ekremah

## Screenshots

Authentic screenshots should be captured from the real running application before submission. Suggested capture sequence is documented in `docs/DEMO_CAPTURE_PLAN.md`.

## License

No project license has been asserted in the repository snapshot. Add the intended license file and README section before submission if the hackathon requires one.
