# Reporting and Exports

The reporting layer consumes deterministic analysis, specialist findings, health scoring, and the renovation roadmap. It performs no new repository access or execution.

It provides typed assessment reports and deterministic JSON, Markdown, and self-contained escaped HTML representations. Reports preserve evidence references, finding IDs, category weights, score explanations, roadmap action IDs, limitations, and manual-review flags.

Repository-derived text is treated as untrusted data. HTML is escaped and contains no scripts, CDNs, remote fonts, images, or executable repository content. Reports are not security certifications and static analysis cannot guarantee runtime correctness, exploitability, freshness, coverage, or production readiness.
