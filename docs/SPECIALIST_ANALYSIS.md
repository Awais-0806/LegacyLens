# Specialist Analysis

LegacyLens runs seven deterministic, static specialists after normalized Phase 3 analysis: architecture, security, dependencies, testing, documentation, maintainability, and modernization.

Findings preserve `Evidence` references, controlled severity (`info`, `low`, `medium`, `high`, `critical`), confidence, impact, recommendation, limitations, manual-review status, and deterministic/inferred classification. Specialists never execute repository code, install dependencies, fetch independently, or expose matched secret values. Each specialist is isolated; failures produce a safe execution error and do not discard other results. Findings are stably ordered by specialist and finding ID.

Absence-based findings are conservative and explicitly limited. Security results are indicators requiring manual review, not confirmed vulnerabilities or CVEs. The engine is static and cannot measure runtime coupling, actual coverage, exploitability, or document quality.
