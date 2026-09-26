# LegacyLens — 3–5 Minute Hackathon Demo Script

## 0:00–0:25 — Problem hook

“Legacy code is expensive to understand before you even change it. Engineers need to know what is actually in the repository, which risks are supported by evidence, what is uncertain, and what should happen first.”

## 0:25–0:45 — Introduce LegacyLens

“LegacyLens turns a public GitHub repository into an evidence-backed modernization assessment. The flow is simple: discover what exists, understand the risks, prioritize what matters, and build a safe renovation path.”

## 0:45–1:10 — Start the analysis

Paste the selected public GitHub URL.

Say:

“I’m submitting a public repository. The server validates the URL, safely ingests the archive, and analyzes the repository without executing its code or installing its dependencies.”

Start analysis and show the general processing stages.

Do not describe these stages as live telemetry; they are presentation states for the request lifecycle.

## 1:10–1:45 — Health score and explanation

Show the overview and score.

Say:

“The score is not a generic AI opinion. It comes from seven specialist analyses, controlled severity and confidence signals, and weighted category scoring.”

Open “Why this score?”.

Point out one positive signal, one limiting factor, and the static-analysis boundary.

Say:

“Missing evidence is not treated as proof of failure. Heuristic indicators are labeled as indicators. Runtime behavior still requires verification.”

## 1:45–2:30 — Findings and risks

Open Specialist Findings.

Search or filter for a finding.

Expand one finding.

Say:

“Every finding carries a specialist, severity, confidence, evidence reference, impact, recommendation, and manual-review status.”

Open prioritized risks.

Say:

“P0 and P1 items are surfaced so an engineer can focus attention instead of reading the repository line by line.”

## 2:30–3:20 — Renovation roadmap

Open the roadmap.

Expand a phase and one action.

Point out:
- priority
- effort
- prerequisites
- expected outcome
- acceptance criteria
- automation safety
- blockers/manual-review requirements

Say:

“LegacyLens does not silently rewrite the repository. It produces a traceable modernization sequence that tells the team what to verify and what to do next.”

## 3:20–3:45 — Canonical exports

Click JSON, Markdown, and HTML exports as time permits.

Say:

“The same backend reporting engine that drives the assessment also produces the canonical engineering exports. The frontend is not inventing a second report format.”

## 3:45–4:20 — Security and trust

Say:

“The ingestion layer rejects unsafe GitHub URLs and redirects, applies archive limits, blocks traversal and links, and never executes repository code. Generated HTML is escaped and self-contained. Errors are sanitized.”

Avoid saying “fully secure,” “zero vulnerabilities,” or “production-proof.”

## 4:20–4:45 — IBM Bob workflow

Say:

“IBM Bob was used as our development and workflow environment. We built LegacyLens in controlled phases: inspect, implement, test, document, review, and harden. The product itself does not depend on an IBM Bob runtime API.”

## 4:45–5:00 — Closing

“LegacyLens helps engineers understand legacy code before they touch it. It makes evidence visible, uncertainty explicit, priorities traceable, and modernization actionable.”
