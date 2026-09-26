# Health Scoring Engine

LegacyLens scoring is deterministic and evidence-backed. Seven categories use centralized weights totaling 100%: architecture 15, security 20, dependencies 15, testing 15, documentation 10, maintainability 15, modernization readiness 10.

Each category starts at 100. Findings apply bounded deductions based on severity, confidence, and evidence strength. Explicit positive signals receive small bounded adjustments. Scores are clamped to 0–100 and weighted into the overall score.

Missing evidence is treated as unknown, not failure. Security indicators remain conservative and may require manual review. Risks are prioritized P0–P3 using severity, confidence, and evidence strength. No runtime behavior, CVEs, coverage, exploitability, or production readiness is inferred.
