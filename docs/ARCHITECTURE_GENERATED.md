# LegacyLens — Architecture Reference

> **Generated from codebase analysis.** Describes the system as implemented.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Repository Layout](#2-repository-layout)
   - [Backend (`backend/`)](#21-backend)
   - [Frontend (`frontend/`)](#22-frontend)
3. [Backend Architecture](#3-backend-architecture)
   - [Entry Point & Middleware Stack](#31-entry-point--middleware-stack)
   - [API Layer](#32-api-layer)
   - [Ingestion Pipeline](#33-ingestion-pipeline)
   - [Deterministic Analysis Layer](#34-deterministic-analysis-layer)
   - [Specialist Analyzer Pipeline](#35-specialist-analyzer-pipeline)
   - [Scoring Engine](#36-scoring-engine)
   - [Roadmap Engine](#37-roadmap-engine)
   - [Report Engine](#38-report-engine)
   - [Database Layer](#39-database-layer)
4. [The 7 Specialist Analyzers](#4-the-7-specialist-analyzers)
5. [Data Flow: GitHub URL → Final Report](#5-data-flow-github-url--final-report)
6. [Frontend Architecture](#6-frontend-architecture)
7. [Key Design Principles](#7-key-design-principles)
8. [Configuration Reference](#8-configuration-reference)

---

## 1. System Overview

LegacyLens is a two-tier web application that performs **static analysis** of public GitHub repositories and produces an evidence-backed engineering health assessment. No repository code is ever executed; all findings are derived from file structure, naming conventions, and content heuristics.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser (Next.js)                        │
│  Landing → /analyze → /overview → /security → /renovation      │
└────────────────────────────┬────────────────────────────────────┘
                             │  POST /api/v1/analyses
                             │  POST /api/v1/reports/export/{format}
┌────────────────────────────▼────────────────────────────────────┐
│                    FastAPI Backend (Python)                      │
│                                                                 │
│  Ingestion → Deterministic Analysis → Specialist Pipeline       │
│           → Scoring Engine → Roadmap Engine → Report Engine     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    GitHub (archive ZIP download)
                    SQLite / PostgreSQL (run history)
```

---

## 2. Repository Layout

### 2.1 Backend

```
backend/
├── app/
│   ├── main.py                    # FastAPI application factory & middleware wiring
│   ├── api/
│   │   ├── router.py              # Aggregates all route groups
│   │   └── routes/
│   │       ├── analysis.py        # POST /analyses — primary end-to-end endpoint
│   │       ├── ingestion.py       # POST /ingest — manifest-only ingestion
│   │       ├── reports.py         # POST /reports/export/{json|markdown|html}
│   │       └── health.py          # GET  /health
│   ├── core/
│   │   ├── config.py              # Pydantic Settings (env-backed, cached)
│   │   ├── errors.py              # AppError domain exception hierarchy
│   │   └── logging.py             # Structured logging configuration
│   ├── middleware/
│   │   ├── security.py            # Security headers, request-size cap, rate limiter
│   │   └── request_context.py     # Injects X-Request-ID per request
│   ├── db/
│   │   ├── models.py              # SQLAlchemy ORM — AnalysisRun table
│   │   ├── session.py             # Engine / Session factory
│   │   └── init_db.py             # Schema bootstrapping (called at startup)
│   ├── services/
│   │   └── url_validation.py      # GitHub URL normalisation & allow-list
│   ├── ingestion/
│   │   ├── service.py             # ingest() and ingest_with_analysis() orchestrators
│   │   ├── fetcher.py             # GitHubFetcher — safe ZIP download with redirect guard
│   │   ├── archive.py             # ZIP extraction with path-traversal & size limits
│   │   ├── manifest.py            # Builds a structured file inventory
│   │   ├── limits.py              # IngestionLimits dataclass (from Settings)
│   │   └── models.py              # IngestionResult, RepositoryMetadata, etc.
│   ├── analysis/
│   │   ├── service.py             # analyze_repository() — deterministic analysis driver
│   │   ├── languages.py           # Language detection by extension + LOC
│   │   ├── frameworks.py          # Technology/framework detection
│   │   ├── dependencies.py        # Manifest & lockfile detection
│   │   ├── testing.py             # Test-file and test-framework heuristics
│   │   ├── documentation.py       # README, CHANGELOG, SECURITY, etc.
│   │   ├── configuration.py       # Docker, CI, .env.example, suspicious files
│   │   ├── metrics.py             # LOC, file sizes, TODO count, deep nesting
│   │   └── models.py              # RepositoryAnalysis and all sub-models
│   ├── specialists/
│   │   ├── base.py                # Specialist abstract base class
│   │   ├── orchestrator.py        # run_specialists() — sequential fan-out
│   │   ├── architecture.py        # ArchitectureSpecialist
│   │   ├── security.py            # SecuritySpecialist
│   │   ├── dependencies.py        # DependencySpecialist
│   │   ├── testing.py             # TestingSpecialist
│   │   ├── documentation.py       # DocumentationSpecialist
│   │   ├── maintainability.py     # MaintainabilitySpecialist
│   │   ├── modernization.py       # ModernizationSpecialist
│   │   ├── models.py              # SpecialistFinding, SpecialistReport, etc.
│   │   └── _util.py               # f() / ev() builder helpers
│   ├── scoring/
│   │   ├── engine.py              # score_repository() — weighted category scoring
│   │   ├── weights.py             # WEIGHTS dict (must sum to 100)
│   │   └── models.py              # ScoringResult, HealthAssessment, RiskPriority, etc.
│   ├── roadmap/
│   │   ├── engine.py              # generate_roadmap() — phased action plan
│   │   └── models.py              # RenovationRoadmap, RoadmapPhase, RenovationAction, etc.
│   ├── reports/
│   │   ├── engine.py              # build_report() + to_json/markdown/html serializers
│   │   └── models.py              # AssessmentReport and all nested report models
│   └── schemas/
│       ├── analysis.py            # AnalyzeRequest (inbound)
│       ├── common.py              # Shared Pydantic schemas
│       └── health.py              # HealthResponse
├── tests/
│   ├── test_analysis_engine.py
│   ├── test_specialists.py
│   ├── test_reports_api.py
│   ├── test_ingestion_security.py
│   ├── test_reports_security.py
│   ├── test_security_headers.py
│   ├── test_url_validation.py
│   ├── test_health.py
│   └── fixtures/                  # python_project, ts_project, empty_project, malformed_project
├── requirements.txt
└── pytest.ini
```

### 2.2 Frontend

```
frontend/
├── app/                           # Next.js App Router pages
│   ├── layout.tsx                 # Root layout — noise overlay + PageTransitions wrapper
│   ├── page.tsx                   # Landing page (static, no API calls)
│   ├── analyze/
│   │   └── page.tsx               # Primary analysis page (client component)
│   ├── overview/                  # Repository overview shell (stub)
│   ├── security/                  # Security findings page (stub)
│   └── renovation/                # Renovation roadmap page (stub)
├── components/
│   ├── Shell.tsx                  # App chrome / navigation wrapper
│   ├── PageTransitions.tsx        # Framer Motion route transitions
│   ├── ArchitectureMap.tsx        # Dynamic (SSR-disabled) file-tree visualisation
│   ├── FindingCard.tsx            # Individual specialist finding card
│   ├── PhaseCard.tsx              # Roadmap phase card
│   ├── RiskRow.tsx                # Risk priority table row
│   ├── StatTile.tsx               # Metric / KPI tile
│   ├── CountUp.tsx                # Animated number counter
│   ├── AnimatedCard.tsx           # Scroll-triggered card animation
│   ├── AnimatedSection.tsx        # Scroll-triggered section animation
│   ├── AuroraBackground.tsx       # Hero gradient effect
│   ├── LandingIcon.tsx            # Icon registry for landing page
│   └── LandingPage.module.css     # Landing page scoped styles
├── lib/
│   └── api.ts                     # Full TypeScript API client + all shared types
├── types/                         # Additional TypeScript type definitions
├── next.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

---

## 3. Backend Architecture

### 3.1 Entry Point & Middleware Stack

[`backend/app/main.py`](../backend/app/main.py) constructs the FastAPI application and attaches four middleware layers in order (outermost to innermost):

| Order | Middleware | Purpose |
|-------|-----------|---------|
| 1 | `SimpleRateLimitMiddleware` | 60 requests / 60 s per client IP + path |
| 2 | `RequestSizeLimitMiddleware` | Rejects bodies > 1 MB |
| 3 | `SecurityHeadersMiddleware` | Adds `X-Content-Type-Options`, `X-Frame-Options`, `Cache-Control: no-store`, etc. |
| 4 | `RequestContextMiddleware` | Attaches `X-Request-ID` for log correlation |
| 5 | `CORSMiddleware` (FastAPI) | Allows only configured `cors_origins` (default: `localhost:3000`) |

The `lifespan` context manager calls [`init_db()`](../backend/app/db/init_db.py) once at startup to bootstrap the SQLite / PostgreSQL schema.

### 3.2 API Layer

All routes are mounted at the prefix `/api/v1` (configurable). Four route groups:

| Route | Method | Description |
|-------|--------|-------------|
| `/api/v1/analyses` | `POST` | Full end-to-end analysis (primary endpoint) |
| `/api/v1/ingest` | `POST` | Manifest-only ingestion (no specialist analysis) |
| `/api/v1/reports/export/{format}` | `POST` | Re-serialise a cached `AssessmentReport` to JSON / Markdown / HTML |
| `/api/v1/health` | `GET` | Health check |

### 3.3 Ingestion Pipeline

Defined in [`backend/app/ingestion/service.py`](../backend/app/ingestion/service.py).

```
raw_url (string)
   │
   ▼
validate_public_github_url()       ← rejects non-github.com, private, or malformed URLs
   │  GitHubRepositoryURL
   ▼
GitHubFetcher.fetch()              ← resolves default branch via GitHub API,
   │                                  downloads archive ZIP,
   │                                  follows redirects only to allowed hosts,
   │                                  enforces max_bytes limit
   │  (zip_bytes, commit_sha)
   ▼
extract_archive()                  ← ZIP extraction inside a TemporaryDirectory,
   │                                  guards path-traversal, per-file size, total size,
   │                                  and file count limits
   │  root: Path
   ▼
build_manifest()                   ← builds structured file inventory
   │  IngestionResult
   ▼
(temp directory cleaned up)
```

**Safety constraints enforced during ingestion:**
- Max repository ZIP size: 100 MB
- Max extracted total size: 250 MB
- Max file count: 10,000
- Max single file size: 10 MB
- Max path length: 512 characters
- Request timeout: 30 seconds
- Redirect allow-list: `github.com`, `codeload.github.com`, `objects.githubusercontent.com`

### 3.4 Deterministic Analysis Layer

[`analyze_repository(root)`](../backend/app/analysis/service.py) walks the extracted directory (excluding `node_modules`, `.git`, `__pycache__`, etc.) and runs seven sub-analysers in parallel within the same call:

| Module | What it produces |
|--------|-----------------|
| [`languages.py`](../backend/app/analysis/languages.py) | `List[LanguageSummary]` — per-language file count, LOC, share % |
| [`frameworks.py`](../backend/app/analysis/frameworks.py) | `List[Technology]` — detected frameworks and tools |
| [`dependencies.py`](../backend/app/analysis/dependencies.py) | `DependencySummary` — manifest files, lockfiles, malformed manifests |
| [`testing.py`](../backend/app/analysis/testing.py) | `TestingSummary` — test files, frameworks, source/test ratio |
| [`documentation.py`](../backend/app/analysis/documentation.py) | `DocumentationSummary` — README, CHANGELOG, SECURITY, etc. |
| [`configuration.py`](../backend/app/analysis/configuration.py) | `ConfigurationSummary` — Docker, CI, `.env.example`, suspicious configs |
| [`metrics.py`](../backend/app/analysis/metrics.py) | `CodeMetrics` — total LOC, largest files, TODO count, deeply nested paths |

All results are assembled into a single [`RepositoryAnalysis`](../backend/app/analysis/models.py) value object that is passed to every subsequent stage.

### 3.5 Specialist Analyzer Pipeline

[`run_specialists(analysis)`](../backend/app/specialists/orchestrator.py) iterates over all seven specialist classes in deterministic order. Each specialist is independent; a failure in one does not halt the others.

```python
SPECIALISTS = [
    ArchitectureSpecialist,
    SecuritySpecialist,
    DependencySpecialist,
    TestingSpecialist,
    DocumentationSpecialist,
    MaintainabilitySpecialist,
    ModernizationSpecialist,
]
```

Each specialist implements `Specialist.analyze(analysis: RepositoryAnalysis) -> SpecialistResult`. Findings from all specialists are merged into a [`SpecialistReport`](../backend/app/specialists/models.py) and sorted by `(specialist, finding_id)`.

See [§4](#4-the-7-specialist-analyzers) for individual specialist details.

### 3.6 Scoring Engine

[`score_repository(analysis, report)`](../backend/app/scoring/engine.py) produces a [`ScoringResult`](../backend/app/scoring/models.py) using a weighted, bounded deduction model:

**Category weights** (must sum to 100):

| Category | Weight |
|----------|--------|
| Security | 20% |
| Architecture | 15% |
| Dependencies | 15% |
| Testing | 15% |
| Maintainability | 15% |
| Documentation | 10% |
| Modernization Readiness | 10% |

**Score formula per category:**

```
raw_score = max(0, min(100,
    100
    - Σ(severity_deduction × confidence_factor × strength_factor)
    + min(8, positive_signals × 2)
))
```

Deduction amounts: `info=0`, `low=3`, `medium=8`, `high=16`, `critical=28`  
Confidence factors: `high=1.0`, `medium=0.65`, `low=0.3`  
Evidence-strength factors: `direct=1.0`, `inferred=0.7`, `heuristic=0.4`

The overall score is the weighted sum of category scores. Each finding is also assigned a risk priority: `P0` (critical + high confidence) through `P3` (low/info).

**Health labels:** `Excellent` (≥90) · `Healthy` (≥75) · `Needs Attention` (≥60) · `At Risk` (≥40) · `Critical Attention` (<40)

### 3.7 Roadmap Engine

[`generate_roadmap(analysis, report, assessment)`](../backend/app/roadmap/engine.py) converts specialist findings into a structured [`RenovationRoadmap`](../backend/app/roadmap/models.py):

- Every finding with severity above `info` becomes a [`RenovationAction`](../backend/app/roadmap/models.py) assigned to one of two base phases: `stabilization` (critical/high) or `documentation_and_observability` (medium/low).
- Two deterministic baseline actions are always injected when triggered: a README creation action (if no README detected) and a characterization-tests action (if no test files detected).
- `critical`/`high` findings that require manual review become [`ModernizationBlocker`](../backend/app/roadmap/models.py) objects that gate earlier phases.
- Actions are de-duplicated by `action_id` and sorted by `(priority, phase, action_id)`.
- A fixed six-phase skeleton (`phase-0` through `phase-5`) provides the narrative sequence from *Baseline and Safety* to *Validation and Governance*.

### 3.8 Report Engine

[`build_report(...)`](../backend/app/reports/engine.py) assembles all upstream results into a single [`AssessmentReport`](../backend/app/reports/models.py):

- **Report ID** is a SHA-256 hash of the repository URL, overall score, and all finding IDs — making identical analyses produce identical IDs.
- Findings are cross-linked to their remediation actions via `source_finding_ids`.
- Three serialisers are provided: `to_json()`, `to_markdown()`, `to_html()` — used by the `/reports/export/{format}` endpoint.

### 3.9 Database Layer

The [`AnalysisRun`](../backend/app/db/models.py) table records each run with `id`, `repository_url`, `commit_sha`, `status`, `error_message`, and `created_at`. The backend supports both PostgreSQL (production) and SQLite (development/testing), configured via `DATABASE_URL` / `SQLITE_DATABASE_URL`.

---

## 4. The 7 Specialist Analyzers

All specialists extend [`Specialist`](../backend/app/specialists/base.py) and receive the fully-populated `RepositoryAnalysis`. They produce zero or more [`SpecialistFinding`](../backend/app/specialists/models.py) objects. Every finding carries `severity`, `confidence`, `evidence`, `impact`, `recommendation`, `limitations`, and a `deterministic_or_inferred` classification.

### 4.1 ArchitectureSpecialist

**File:** [`backend/app/specialists/architecture.py`](../backend/app/specialists/architecture.py)  
**Input fields used:** `entry_points`, `metrics.deeply_nested_paths`, `documentation.categories`

| Finding ID | Trigger | Severity |
|-----------|---------|---------|
| `architecture.entrypoint-concentration` | More than `max(3, file_count/4)` conventional entry points detected | `low` |
| `architecture.deep-nesting` | `metrics.deeply_nested_paths` is non-empty | `low` |
| `architecture.missing-docs` | No architecture documentation category signal | `low` |

### 4.2 SecuritySpecialist

**File:** [`backend/app/specialists/security.py`](../backend/app/specialists/security.py)  
**Input fields used:** `configuration.suspicious_files`, `configuration.env_examples`, `documentation.categories`

| Finding ID | Trigger | Severity |
|-----------|---------|---------|
| `security.suspicious-config` | Suspicious configuration filenames detected | `low` |
| `security.no-env-example` | No `.env.example`-style file found | `low` |
| `security.no-security-docs` | No `SECURITY.md` or equivalent detected | `low` |

### 4.3 DependencySpecialist

**File:** [`backend/app/specialists/dependencies.py`](../backend/app/specialists/dependencies.py)  
**Input fields used:** `dependency_summary.manifest_files`, `dependency_summary.lockfiles`, `dependency_summary.malformed_files`

| Finding ID | Trigger | Severity |
|-----------|---------|---------|
| `dependencies.no-lockfile` | Manifests exist but no lockfile | `medium` |
| `dependencies.malformed-manifest` | At least one manifest could not be parsed | `medium` |

### 4.4 TestingSpecialist

**File:** [`backend/app/specialists/testing.py`](../backend/app/specialists/testing.py)  
**Input fields used:** `testing.test_files`, `testing.test_to_source_ratio`, `testing.source_file_count`

| Finding ID | Trigger | Severity |
|-----------|---------|---------|
| `testing.no-obvious-tests` | No test files detected | `medium` |
| `testing.low-test-density` | `test_to_source_ratio < 0.1` with source files present | `low` |

### 4.5 DocumentationSpecialist

**File:** [`backend/app/specialists/documentation.py`](../backend/app/specialists/documentation.py)  
**Input fields used:** `documentation.has_readme`, `documentation.categories`

| Finding ID | Trigger | Severity |
|-----------|---------|---------|
| `documentation.missing-readme` | No README detected | `medium` |
| `documentation.coverage-gaps` | Any documentation category signal is `False` | `low` |

### 4.6 MaintainabilitySpecialist

**File:** [`backend/app/specialists/maintainability.py`](../backend/app/specialists/maintainability.py)  
**Input fields used:** `metrics.largest_files`, `metrics.todo_count`

| Finding ID | Trigger | Severity |
|-----------|---------|---------|
| `maintainability.large-files` | Any file exceeds 50,000 bytes | `medium` |
| `maintainability.todo-concentration` | `metrics.todo_count > 0` | `low` |

### 4.7 ModernizationSpecialist

**File:** [`backend/app/specialists/modernization.py`](../backend/app/specialists/modernization.py)  
**Input fields used:** `dependency_summary`, `testing.test_files`, `documentation.has_readme`

| Finding ID | Trigger | Severity |
|-----------|---------|---------|
| `modernization.reproducible-deps` | Manifests exist, no lockfile | `medium` |
| `modernization.characterization-tests` | No test files detected | `medium` |
| `modernization.onboarding-docs` | No README detected | `low` |

> **Note:** The Modernization specialist intentionally overlaps with Dependencies, Testing, and Documentation specialists. It surfaces the same signals from a *change-readiness* perspective, synthesising cross-cutting upgrade concerns rather than simply flagging gaps.

---

## 5. Data Flow: GitHub URL → Final Report

The complete pipeline is executed synchronously inside a single HTTP request to `POST /api/v1/analyses`.

```
Client
  │
  │  POST /api/v1/analyses
  │  { "repository_url": "https://github.com/owner/repo" }
  │
  ▼
[1] URL Validation
    validate_public_github_url(raw_url)
    → GitHubRepositoryURL(owner, repo, canonical_url)

  │
  ▼
[2] Repository Fetch
    GitHubFetcher.fetch(repo)
    → Resolve default branch via GitHub API
    → Download https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip
    → Follow redirects (allowed hosts only)
    → Enforce max_bytes (100 MB)
    → Returns (zip_bytes, commit_sha)

  │
  ▼
[3] Archive Extraction                    [TemporaryDirectory]
    extract_archive(zip_bytes, root, limits)
    → Validate each entry: no path traversal, size limits, count limits
    → Write files to temp dir

  │
  ▼
[4] Deterministic Analysis
    analyze_repository(root) → RepositoryAnalysis
    ├── detect_languages()
    ├── detect_technologies()
    ├── analyze_dependencies()
    ├── analyze_testing()
    ├── analyze_documentation()
    ├── analyze_configuration()
    └── analyze_metrics()
    (temp directory cleaned up after this step)

  │
  ▼
[5] Specialist Pipeline
    run_specialists(RepositoryAnalysis) → SpecialistReport
    ├── ArchitectureSpecialist.analyze()    → 0–3 findings
    ├── SecuritySpecialist.analyze()        → 0–3 findings
    ├── DependencySpecialist.analyze()      → 0–2 findings
    ├── TestingSpecialist.analyze()         → 0–2 findings
    ├── DocumentationSpecialist.analyze()   → 0–2 findings
    ├── MaintainabilitySpecialist.analyze() → 0–2 findings
    └── ModernizationSpecialist.analyze()   → 0–3 findings
    Findings sorted, executions logged, failures isolated.

  │
  ▼
[6] Scoring
    score_repository(RepositoryAnalysis, SpecialistReport) → ScoringResult
    → Weighted deduction model across 7 categories
    → Positive signal bonuses
    → Risk priorities (P0–P3) assigned to each finding
    → HealthAssessment with overall_score (0–100) and health_label

  │
  ▼
[7] Roadmap Generation
    generate_roadmap(RepositoryAnalysis, SpecialistReport, HealthAssessment)
    → RoadmapResult
    → One RenovationAction per non-info finding
    → Baseline deterministic actions (README, tests) injected if triggered
    → Blockers identified from critical/high security findings
    → Six-phase roadmap skeleton (phase-0 through phase-5)

  │
  ▼
[8] Report Assembly
    build_report(repo_url, repo_name, analysis, specialists, scoring, roadmap)
    → AssessmentReport
    → Deterministic report_id (SHA-256)
    → Findings cross-linked to roadmap actions
    → ExecutiveReport, CategoryReport[], FindingReport[], RiskPriority[]

  │
  ▼
[9] HTTP Response
    {
      "analysis_id": "<uuid>",
      "status": "completed",
      "repository": { ... },
      "analysis": RepositoryAnalysis,
      "specialists": SpecialistReport,
      "assessment": ScoringResult,
      "roadmap": RoadmapResult,
      "report": AssessmentReport
    }

  │
  ▼
[10] Client renders results
     /analyze page — score ring, stat tiles, finding cards,
     architecture map, risk table, phase cards, export buttons

[11] Optional: Export
     POST /api/v1/reports/export/{json|markdown|html}
     → Client sends AssessmentReport back to get serialised file download
```

---

## 6. Frontend Architecture

The frontend is a **Next.js 15 App Router** application written in TypeScript, styled with Tailwind CSS and `globals.css` utility classes.

### Pages

| Route | File | Type | Purpose |
|-------|------|------|---------|
| `/` | [`app/page.tsx`](../frontend/app/page.tsx) | Server Component | Static marketing / landing page |
| `/analyze` | [`app/analyze/page.tsx`](../frontend/app/analyze/page.tsx) | Client Component | Full analysis UI — submits URL, polls loading stages, renders all results |
| `/overview` | [`app/overview/page.tsx`](../frontend/app/overview/page.tsx) | Server Component | Overview shell (stub) |
| `/security` | `app/security/page.tsx` | Server Component | Security findings shell (stub) |
| `/renovation` | `app/renovation/` | — | Renovation roadmap (stub) |

### API Client

[`frontend/lib/api.ts`](../frontend/lib/api.ts) is the single source of truth for all backend communication and TypeScript type definitions. It exports:

- `apiRequest<T>()` — generic fetch wrapper with error normalisation
- `exportCanonicalReport()` — submits an `AssessmentReport` for file download
- All shared types mirroring the backend Pydantic schemas (`AnalyzeResponse`, `SpecialistFinding`, `HealthAssessment`, `RenovationRoadmap`, etc.)

The API base URL is configured via `NEXT_PUBLIC_API_BASE_URL` (default: `http://localhost:8000/api/v1`).

### Key Components

| Component | Purpose |
|-----------|---------|
| [`Shell`](../frontend/components/Shell.tsx) | App chrome, navigation, layout wrapper |
| [`ArchitectureMap`](../frontend/components/ArchitectureMap.tsx) | Dynamic (SSR-disabled) file-tree visualisation of the repository structure |
| [`FindingCard`](../frontend/components/FindingCard.tsx) | Renders a single `SpecialistFinding` with severity badge, evidence, and recommendation |
| [`PhaseCard`](../frontend/components/PhaseCard.tsx) | Renders a `RoadmapPhase` with its actions and exit criteria |
| [`RiskRow`](../frontend/components/RiskRow.tsx) | Table row for a `RiskPriority` item |
| [`StatTile`](../frontend/components/StatTile.tsx) | KPI metric tile (file count, LOC, health score, etc.) |
| [`CountUp`](../frontend/components/CountUp.tsx) | Animated integer counter for the health score ring |
| [`PageTransitions`](../frontend/components/PageTransitions.tsx) | Framer Motion route transition wrapper |

---

## 7. Key Design Principles

**1. No code execution.** The entire pipeline operates on file paths, names, sizes, and text content. No repository code is compiled, interpreted, or run at any stage.

**2. Evidence-backed findings.** Every `SpecialistFinding` carries an `evidence` list referencing the exact paths or indicators that triggered it, plus `limitations` disclosing what static analysis cannot confirm.

**3. Deterministic and reproducible.** Given the same repository snapshot, the pipeline produces the same report ID, the same score, and the same findings. The `deterministic: true` flag on `ScoringResult` and `AssessmentReport` makes this explicit.

**4. Fail-safe specialists.** The orchestrator wraps each specialist in a `try/except`. A failing specialist logs a warning and contributes zero findings rather than aborting the analysis.

**5. Bounded scoring.** Category scores are clamped to `[0, 100]`. Positive signals add at most 8 points, preventing "double recovery" from offsetting high-severity issues.

**6. Defence in depth (ingestion).** Multiple independent guards at the network, archive, and filesystem layers prevent path traversal, zip bombs, resource exhaustion, and SSRF.

---

## 8. Configuration Reference

All configuration is managed via [`backend/app/core/config.py`](../backend/app/core/config.py) (`pydantic-settings`, reads from `.env`).

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Environment tag |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `API_PREFIX` | `/api/v1` | API route prefix |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |
| `MAX_REQUEST_BODY_BYTES` | `1,048,576` | Request body size cap (1 MB) |
| `RATE_LIMIT_REQUESTS` | `60` | Requests per window per client |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | Rate limit window |
| `MAX_REPOSITORY_SIZE_MB` | `100` | Max ZIP download size |
| `MAX_FILE_SIZE_MB` | `10` | Max single extracted file |
| `MAX_FILE_COUNT` | `10,000` | Max files extracted |
| `MAX_TOTAL_EXTRACTED_SIZE_MB` | `250` | Max total extracted bytes |
| `MAX_PATH_LENGTH` | `512` | Max path length in archive |
| `INGESTION_TIMEOUT_SECONDS` | `30` | HTTP fetch timeout |
| `DATABASE_URL` | PostgreSQL connection string | Production database |
| `SQLITE_DATABASE_URL` | `sqlite:///./legacylens.db` | Development/test database |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000/api/v1` | Frontend API base (`.env.local`) |
