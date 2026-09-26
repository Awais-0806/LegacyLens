# IBM Bob 2.0 Development Workflow

## Scope and accuracy

IBM Bob is documented here as the **development/workflow environment used to build LegacyLens**. LegacyLens does not claim to call an IBM Bob runtime API, SDK, or service from the product itself.

## How the project was developed

The project was built through explicit engineering phases rather than a single monolithic generation pass:

1. Workspace inspection and architecture foundation.
2. Safe repository ingestion and archive-security controls.
3. Deterministic static analysis.
4. Seven specialist analyzers.
5. Health scoring and risk prioritization.
6. Renovation roadmap generation.
7. Reporting and canonical export logic.
8. Interactive assessment dashboard.
9. Production hardening and export API validation.
10. Final demo/submission preparation.

Within that workflow, Bob-supported development activities were used for planning, implementation assistance, focused engineering work, iterative debugging, test-driven verification, documentation, and review of security/edge-case behavior.

## Agent/Ask/Plan usage

Where these Bob modes were used, the working pattern was:

- **Plan / planning context:** decompose the next phase, identify dependencies, and preserve existing architecture.
- **Agent / implementation context:** make targeted changes inside the current repository and run the relevant verification commands.
- **Ask / review context:** inspect source, reason about defects, validate security boundaries, and clarify implementation behavior.

The workflow intentionally avoided claiming undocumented Bob APIs or runtime integrations.

## Parallel and focused work

Independent concerns were kept separated where practical: ingestion security, specialist analysis, scoring, roadmap logic, reporting, frontend presentation, and final hardening. This allowed each phase to have its own implementation status and regression check.

## Verification loop

Each engineering phase followed the same discipline:

**inspect → implement → test → inspect results → document status → continue**

Claims in the project documentation are based on commands actually executed. Environment-dependent checks are explicitly labeled rather than converted into assumed successes.

## Rollback/version control

No unsupported rollback mechanism is claimed here. The repository is intended to be managed with normal source-control/versioning practices, but this document records only capabilities actually used during development.

## Final distinction

**LegacyLens is the product. IBM Bob is the development workflow/tooling context.** This distinction should remain explicit in the hackathon presentation.
