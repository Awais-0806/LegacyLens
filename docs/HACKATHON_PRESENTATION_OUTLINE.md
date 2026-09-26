# LegacyLens — Hackathon Presentation Outline

## Slide 1 — Title

**LegacyLens**

Understand legacy code. See the risks. Modernize with confidence.

Speaker notes: LegacyLens converts a public GitHub repository into an evidence-backed modernization assessment.

## Slide 2 — The Problem

- Legacy repositories are expensive to understand.
- Risk is often mixed with assumption.
- Teams need a repeatable way to prioritize modernization work.
- Before changing code, engineers need evidence and context.

Speaker notes: Focus on uncertainty and engineering time, not unsupported claims about industry-wide statistics.

## Slide 3 — The Solution

**DISCOVER → UNDERSTAND → PRIORITIZE → MODERNIZE**

- Safe repository ingestion
- Deterministic static analysis
- Seven specialist perspectives
- Health score and risk priorities
- Renovation roadmap
- Canonical engineering reports

Speaker notes: Emphasize that the product is decision support, not autonomous source rewriting.

## Slide 4 — How LegacyLens Works

Show the pipeline:

Repository URL → Safe ingestion → Deterministic analysis → Specialists → Scoring → Roadmap → Reports/UI

Speaker notes: Repository code is not executed and dependencies are not installed during analysis.

## Slide 5 — Architecture

Show:

Next.js dashboard → FastAPI → ingestion + analysis domain → specialists → scoring → roadmap → reporting

Speaker notes: Keep the architecture intentionally simple. No unnecessary queues, microservices, or cloud infrastructure.

## Slide 6 — Analysis and Scoring

Show the seven categories and weights:

Architecture 15%, Security 20%, Dependencies 15%, Testing 15%, Documentation 10%, Maintainability 15%, Modernization Readiness 10%.

Speaker notes: Score explanations are derived from backend assessment data. Confidence and evidence strength matter.

## Slide 7 — Renovation Roadmap

Show:
- P0–P3 priorities
- quick wins
- blockers
- prerequisites
- acceptance criteria
- automation safety

Speaker notes: The roadmap is designed for human-reviewed modernization, not blind automation.

## Slide 8 — Security and Trust

- HTTPS GitHub URL validation
- Redirect rejection
- Archive traversal/link protections
- Resource limits
- No repository execution
- Sanitized errors
- Escaped standalone HTML exports

Speaker notes: Say “security-conscious” and “defense-in-depth”; do not claim absolute security.

## Slide 9 — IBM Bob Development Process

- Phased planning
- Focused implementation
- Iterative debugging
- Regression testing
- Security review
- Documentation and hardening

Speaker notes: IBM Bob is the development workflow/tooling context, not a runtime dependency of LegacyLens.

## Slide 10 — Demo / Value / Next Steps

Demo sequence:

1. Submit repository
2. Score
3. Explainability
4. Findings
5. P0/P1 risks
6. Roadmap
7. Export report

Future work:
- persistent report history
- deeper runtime/security validation
- browser-validated production deployment
- additional repository providers only if required

Speaker notes: Clearly separate current implementation from future work.
