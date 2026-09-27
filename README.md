# LegacyLens — Evidence-backed repository intelligence

> **Understand legacy code. Modernize with confidence.**

![Next.js](https://img.shields.io/badge/Next.js-15.5.7-black?logo=next.js)
![React](https://img.shields.io/badge/React-19.1.1-149eca?logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7.3-3178c6?logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12.10-3776ab?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128.2-009688?logo=fastapi&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-a3e635)](#license)

LegacyLens turns a public GitHub repository into an evidence-backed modernization assessment: what is in the codebase, how healthy it is, which risks matter first, and what to renovate next. It is built for engineers inheriting code they did not write — every finding carries file-path evidence and an explicit source classification, so a heuristic signal is never presented as a confirmed defect. Analysis is fully deterministic (no LLM in the production path), the scoring arithmetic is published in the UI, and the output is a phased renovation roadmap rather than a bare list of complaints.

## Screenshots

![Landing page](docs/screenshots/01-landing.png)
*01 — Landing page: aurora background and the three-step workflow.*

![Repository input](docs/screenshots/02-analyze-input.png)
*02 — Repository input on `/analyze`.*

![Processing state](docs/screenshots/03-loading.png)
*03 — Processing state with the skeleton layout.*

![Assessment overview](docs/screenshots/04-assessment-overview.png)
*04 — Assessment overview: health score, category scores, and the "Why this score?" panel.*

![Specialist findings](docs/screenshots/05-specialist-findings.png)
*05 — Specialist findings with evidence references and source classification.*

![Architecture map](docs/screenshots/06-architecture-map.png)
*06 — Interactive architecture map (force-directed graph).*

![Renovation roadmap](docs/screenshots/07-renovation-roadmap.png)
*07 — Renovation roadmap phases and actions.*

![Exports](docs/screenshots/08-exports.png)
*08 — Canonical exports: JSON, Markdown, HTML.*

All screenshots were captured from the running application analyzing `https://github.com/pallets/flask`.

## Features

- **Deterministic static analysis** — no LLM in the production path; the same input produces the same output.
- **7 specialist analyzers** — Architecture, Security, Dependencies, Testing, Documentation, Maintainability, Modernization Readiness.
- **Transparent scoring** — an explainable "Why this score?" panel shows the arithmetic, positive signals, and limitations.
- **Prioritized P0–P3 risks** — each with evidence references and a manual-review flag where applicable.
- **Phased 6-step renovation roadmap** — actions with effort, prerequisites, acceptance criteria, and automation safety.
- **Interactive Architecture Map** — force-directed graph of languages, technologies, and entry points, with per-node findings and category scores.
- **Score count-up and findings stagger animations** — framer-motion, fully honoring `prefers-reduced-motion`.
- **Canonical exports** — JSON, Markdown, and HTML generated server-side from the same report object the dashboard renders.
- **Security-first ingestion** — HTTPS-only, redirect allowlist, traversal-safe extraction, and no repository code execution.

## Architecture

```text
          Public GitHub repository URL
  (HTTPS only · host exactly github.com · owner/repo)
                        │
                        ▼
    ══════════ Backend · FastAPI 0.128 · Python 3.12 ══════════

              ┌───────────────────┐
              │     Ingestion     │  URL validation, bounded archive
              │                   │  download, traversal-safe extract
              └─────────┬─────────┘  into a temporary workspace
                        ▼
              ┌───────────────────┐
              │  Deterministic    │  languages, technologies, metrics,
              │     Analysis      │  entry points, testing/doc signals
              └─────────┬─────────┘
                        ▼
              ┌───────────────────┐
              │   7 Specialists   │  architecture · security · dependencies
              │                   │  testing · documentation ·
              └─────────┬─────────┘  maintainability · modernization
                        ▼
              ┌───────────────────┐
              │      Scoring      │  7 weighted categories, 0–100,
              │                   │  severity × confidence × evidence
              └─────────┬─────────┘
                        ▼
              ┌───────────────────┐
              │      Roadmap      │  6 phases, P0–P3 actions, blockers,
              │                   │  quick wins, acceptance criteria
              └─────────┬─────────┘
                        ▼
              ┌───────────────────┐
              │   Report Build    │  canonical JSON, plus Markdown and
              │                   │  standalone HTML exports
              └─────────┬─────────┘
                        │
    ════════════════════┼════════════════════════════════════════
                        ▼
    ══ Frontend · Next.js 15.5.7 · React 19.1 · TypeScript 5.7 ══

         • Assessment dashboard — score, risk level, category breakdown
         • "Why this score?" — explanation, positive signals, limitations
         • Specialist findings — filterable, each with evidence paths
         • Prioritized risks — P0–P3 with recommendations
         • Architecture Map — force-directed graph, click for evidence
         • Renovation roadmap — phases, actions, blockers, quick wins
         • Exports — JSON / Markdown / HTML, downloaded as files
```

The frontend renders the backend assessment exactly as returned; it never recomputes scores or invents findings.

### Tech stack

**Backend**

- FastAPI 0.128.2
- Python 3.12.10
- SQLAlchemy 2.0.50 + SQLite (local/test), PostgreSQL configuration for non-development environments
- Pydantic 2.13.4 / pydantic-settings 2.10.1
- httpx 0.28.1
- pytest 9.0.2 — 31 tests passing

**Frontend**

- Next.js 15.5.7 (App Router)
- React 19.1.1
- TypeScript 5.7.3 (`"strict": true`)
- Tailwind CSS 3.4.17
- Framer Motion 13.4.4
- react-force-graph-2d 1.29.1

## The 7 Specialists

| Specialist | What it detects |
|---|---|
| `architecture` | Entry-point concentration, deep module nesting, missing architecture-documentation signals |
| `security` | Conservative configuration indicators — suspicious config filenames, missing `.env.example`, missing security docs. Not vulnerability scanning |
| `dependencies` | Missing lockfiles next to manifests, malformed or unparseable dependency manifests |
| `testing` | Absent test files, test-to-source ratio below 0.1 |
| `documentation` | Missing README, per-category documentation coverage gaps |
| `maintainability` | Oversized source files (> 50 KB), TODO/FIXME debt markers |
| `modernization` | Modernization readiness — reproducible dependencies, characterization tests, onboarding documentation |

Every finding reports its evidence references (the file paths behind the claim) and a source classification of `deterministic` or `inferred`. Findings that cannot be settled from static evidence are flagged `requires_manual_review` instead of being asserted.

## Scoring Model

The health score is 0–100 and is fully deterministic:

1. **Each of the seven categories starts at 100.**
2. **Bounded severity deductions** are applied per finding: info 0, low 3, medium 8, high 16, critical 28.
3. **Confidence and evidence-strength adjustments** scale each deduction — confidence: high 1.0, medium 0.65, low 0.3; evidence: direct/verified 1.0, inferred 0.7, heuristic-with-manual-review 0.4. Weak evidence therefore costs less than proof.
4. **Small positive-signal bonuses** add back up to 8 points per category (`min(8, 2 × signal count)`) for verified good practice such as CI configuration or a lockfile.
5. **Category scores are weighted to 100** and summed, then clamped to 0–100.

| Category | Weight |
|---|---:|
| Architecture | 15% |
| Security | 20% |
| Dependencies | 15% |
| Testing | 15% |
| Documentation | 10% |
| Maintainability | 15% |
| Modernization readiness | 10% |

Labels: ≥ 90 Excellent · ≥ 75 Healthy · ≥ 60 Needs Attention · ≥ 40 At Risk · below 40 Critical Attention. Risks are prioritized P0 (critical, high confidence, direct evidence) through P3. The dashboard's "Why this score?" panel exposes the same explanation, positive signals, and limitations the backend returned.

## Renovation Roadmap

The roadmap engine emits six fixed phases and places evidence-linked actions into them:

| # | Phase | Purpose |
|---|---|---|
| 0 | **Baseline and Safety** | Establish a safe starting point before any change |
| 1 | **Stabilization** | Critical/high findings and characterization-test baselines |
| 2 | **Documentation and Observability** | README, onboarding, and observability gaps |
| 3 | **Structural Refactoring** | Reserved for structural work once the codebase is stable |
| 4 | **Incremental Modernization** | Reserved for staged modernization steps |
| 5 | **Validation and Governance** | Reserved for verification and governance closure |

Every action carries priority (P0–P3), effort (XS–XL), impact, risk, rationale, evidence references, prerequisites, expected outcome, acceptance criteria, and an automation-safety classification (`safe_to_automate`, `human_review_required`, or `do_not_automate`). Critical or high findings that require manual review — and security findings — additionally surface as explicit blockers. Quick wins are XS/S effort with low risk.

## Report Exports

Three canonical formats are generated server-side from the same report object the dashboard renders:

- **JSON** — the canonical machine-readable assessment.
- **Markdown** — a portable engineering report.
- **HTML** — a standalone document. Every interpolated string is escaped and it references no external scripts, fonts, images, or CDNs. **HTML is downloaded as a file and is never injected into the application.**

Downloads use fixed filenames (`legacylens-assessment.json|md|html`) via `Content-Disposition: attachment`, and the frontend triggers them as blob downloads. The dashboard contains no `dangerouslySetInnerHTML`.

## Security Model

- **HTTPS-only repository URLs**; the host must be exactly `github.com` with an `owner/repo` path.
- **Credential rejection** — URLs embedding usernames or tokens are refused.
- **Custom-port rejection** — only the default HTTPS port is accepted.
- **Query string and fragment rejection.**
- **Redirect allowlist** — redirects are followed manually and only to `github.com`, `codeload.github.com`, and `objects.githubusercontent.com` (max 5 hops); anything else is rejected.
- **Archive traversal protection** — zip-slip defenses reject `..` segments, absolute paths, and Windows drive-letter paths, and every resolved path is verified to stay inside the temporary workspace.
- **Symlink and hardlink rejection**, plus NUL-byte rejection in archive entry names.
- **File count and size limits** — 100 MB download, 10 MB per file, 250 MB total extracted, 10,000 files, 512-character paths, 30 s fetch timeout, 1 MiB request bodies.
- **No repository code execution** — the repository is read, never run.
- **No dependency installation** from the inspected repository.
- **Rate limiting** — in-process, 60 requests per 60 s window per client IP and path, answered with `429` and `Retry-After`.
- **Restricted CORS** — default origin `http://localhost:3000`, credentials disabled, GET/POST only. Origins match exactly, so `http://127.0.0.1:3000` is a different origin and is rejected unless added to `CORS_ORIGINS`.
- **Sanitized exceptions** — client-facing errors are generic messages plus a request id; stack traces stay server-side.
- **No `dangerouslySetInnerHTML`** anywhere in the frontend.
- **HTML export never injected** — it is escaped, self-contained, and delivered as a download.
- Security headers on every response: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, `Permissions-Policy`, `Cache-Control: no-store`.

These are conservative safeguards for a static-analysis tool, not a claim that any analyzed repository is vulnerability-free.

## IBM Bob 2.0 Usage

LegacyLens was developed with IBM Bob 2.0 as the primary AI development workflow partner. 10 task sessions were completed across two team members. Evidence (screenshots of every session) is available in [`bob_sessions/`](bob_sessions/).

What Bob was used for:

- **Security reviews** — SSRF and redirect-safety review of `backend/app/ingestion/fetcher.py` (full report: `bob_sessions/awais/ssrf-redirect-safety-fetcher-py-security-report.html`), plus URL-validation review.
- **Architecture documentation generation** — see `docs/ARCHITECTURE_GENERATED.md`.
- **Bug detection** — a dedicated backend bug-hunt session (`bob_sessions/awais/03-bug-hunt.png`).
- **TypeScript type-safety audits** — frontend review session (`bob_sessions/awais/04-frontend-review.png`), which is where the finding evidence-field type mismatch was corrected.
- **Test coverage analysis** — `bob_sessions/awais/05-test-coverage.png`.
- **Dependency analyzer review** — `bob_sessions/ekremah/03-dependency-analysis.png`.
- **Scoring, roadmap, and export-API reviews** — `bob_sessions/ekremah/01-scoring-review.png`, `02-roadmap-review.png`, `04-export-api-review.png`.

| Member | Sessions |
|---|---|
| Awais Jabbar | security review · architecture · bug hunt · frontend review · test coverage |
| Muhammad Ekremah | scoring review · roadmap review · dependency analysis · export API review · URL validation |

The working pattern in every session was the same loop: inspect source, implement a targeted change, run verification commands, inspect results, document status, continue. Claims in this repository's documentation are limited to commands actually executed and behavior actually observed. LegacyLens itself does not call any IBM Bob runtime API or SDK — Bob is the development workflow, LegacyLens is the product. See `docs/BOB_WORKFLOW.md` for the project-specific record.

## Local Setup

### Backend (Windows)

```bat
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
set APP_ENV=test
set DATABASE_URL=sqlite:///./legacylens.db
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Verify with `curl http://127.0.0.1:8000/api/v1/health` — expect `{"status":"ok","service":"LegacyLens","version":"0.1.0","database":"ok"}`.

### Frontend (Windows, new terminal)

```bat
cd frontend
npm install
echo NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1 > .env.local
npm run dev
```

Open: **http://localhost:3000**

Open the app through the `localhost` hostname, not `http://127.0.0.1:3000`. The backend's default CORS allowlist contains exactly `http://localhost:3000`, so an IP-based origin fails the preflight for `POST /api/v1/analyses` with `400` and the analysis never starts. To serve the frontend from a different origin, start the backend with `set CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000` first.

Live GitHub analysis requires outbound network access from the machine running the backend.

## Environment Variables

Backend settings live in `backend/app/core/config.py` (pydantic-settings; every value has a working default).

| Variable | Code default | Local setup value | Purpose |
|---|---|---|---|
| `APP_ENV` | `development` | `test` | Environment mode |
| `DATABASE_URL` | PostgreSQL DSN | `sqlite:///./legacylens.db` | Primary database for non-development environments |
| `SQLITE_DATABASE_URL` | `sqlite:///./legacylens.db` | — | Local/test database |
| `CORS_ORIGINS` | `http://localhost:3000` | — | Allowed browser origins (comma-separated, matched exactly) |
| `API_PREFIX` | `/api/v1` | — | API route prefix |
| `LOG_LEVEL` | `INFO` | — | Logging verbosity |
| `MAX_REQUEST_BODY_BYTES` | `1048576` | — | Request body cap (1 MiB) |
| `RATE_LIMIT_REQUESTS` / `RATE_LIMIT_WINDOW_SECONDS` | `60` / `60` | — | Rate limit per client IP + path |
| `MAX_REPOSITORY_SIZE_MB` | `100` | — | Archive download cap |
| `MAX_FILE_SIZE_MB` | `10` | — | Per-file extraction cap |
| `MAX_TOTAL_EXTRACTED_SIZE_MB` | `250` | — | Total extraction cap |
| `MAX_FILE_COUNT` / `MAX_EXTRACTION_FILES` | `10000` / `10000` | — | File-count caps |
| `MAX_PATH_LENGTH` | `512` | — | Path length cap |
| `INGESTION_TIMEOUT_SECONDS` | `30` | — | Fetch timeout |

Frontend:

| Variable | Code default | Purpose |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000/api/v1` | Backend API base URL, inlined at build time |

Never put backend secrets in `NEXT_PUBLIC_*` variables — they are embedded in the client bundle.

## API Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/health` | Health check — service status, version, database connectivity |
| `POST` | `/api/v1/analyses` | Run full analysis: ingestion → analysis → specialists → scoring → roadmap → report. Body: `{ "repository_url": "https://github.com/owner/repo" }` |
| `POST` | `/api/v1/repositories/ingest` | Ingest a validated GitHub URL into a temporary workspace |
| `POST` | `/api/v1/reports/export/json` | Export JSON |
| `POST` | `/api/v1/reports/export/markdown` | Export Markdown |
| `POST` | `/api/v1/reports/export/html` | Export HTML |
| `GET` | `/docs` | FastAPI OpenAPI documentation |

Export endpoints accept the validated report object returned by the analysis pipeline. Reports are request-scoped; there is no persistent report store.

## Tests

Backend — **31 tests passing** across the analysis engine, specialists, scoring, ingestion security, URL validation, security headers, and export behavior:

```bat
cd backend
pytest -q
```

Frontend types:

```bat
cd frontend
npx tsc --noEmit
```

Frontend production build:

```bat
cd frontend
npm run build
```

Browser-level behavior — the analysis flow, architecture-map interactions, 375 px responsive layout, reduced-motion rendering, and zero console errors — is verified against the running application with a Chrome DevTools Protocol harness.

## Demo Workflow

1. Start the backend (`uvicorn` on port 8000) and confirm `GET /api/v1/health` returns `ok`.
2. Start the frontend (`npm run dev` on port 3000).
3. Open **http://localhost:3000** — use the `localhost` hostname so CORS matches.
4. Paste a public GitHub URL, e.g. `https://github.com/pallets/flask`, and run the assessment.
5. Review the health score, risk level, and the "Why this score?" explanation with its positive signals and limitations.
6. Explore findings and P0–P3 risks, then open the architecture map (click a node for its evidence, switch By health / By size, try fullscreen), then walk the roadmap phases.
7. Export the report in any of the three formats and open the HTML file directly.

If network access is unavailable, use the deterministic local fixtures exercised by the backend test suite and label the demonstration as a fixture run — never present fixture output as a live GitHub analysis.

## Limitations

- **Static analysis only** — no code execution, no runtime behavior, no DAST/SAST vulnerability scanning.
- **Scores reflect detectable evidence; absence is not proof** — a missing file is a signal, not a confirmed defect.
- **Manual review remains required** for high/critical findings, and those findings are flagged as such.
- **No LLM in the production path** — deterministic by design, which also means no semantic understanding of code intent.
- **Language and technology detection is based on file signatures** and manifest evidence, not on compilation or execution.
- Reports are request-scoped; there is no persisted report history.
- The fetched commit SHA is not pinned in responses in the current implementation.
- Rate limiting is in-process and intended for local/sandbox deployment, not horizontally scaled production.
- The architecture map caps display at 8 languages, 12 technologies, and 12 entry points, and says so in the UI when items are hidden.

## Hackathon Submission

- **Event:** IBM Bob 2.0 Hackathon (September 2026)
- **Platform:** lablab.ai
- **Team:** AWAIS-EKREMAH
- **Members:** Awais Jabbar, Muhammad Ekremah
- **Repository:** _public GitHub URL to be added once the repository is published_
- **Session evidence:** [`bob_sessions/`](bob_sessions/) — 10 sessions, 5 per member
- **Submission checklist:** `docs/SUBMISSION_CHECKLIST.md`

## License

MIT License — Copyright (c) 2026 AWAIS-EKREMAH. Stated inline here; no separate `LICENSE` file is committed.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Team

- **Awais Jabbar** — full-stack development, architecture
- **Muhammad Ekremah** — backend review, testing, quality

## Acknowledgments

Built with IBM Bob 2.0 as the AI development partner.
