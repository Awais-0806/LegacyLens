# LegacyLens — Demo Capture Plan

## Capture rule

Capture screenshots and video only from the real running application. Never fabricate scores, findings, repository results, or export files.

## Primary capture sequence

1. **Landing page** — clean opening frame with LegacyLens name/tagline.
2. **Repository input** — public GitHub URL entered before submission.
3. **Loading state** — processing stages visible; do not imply real-time telemetry.
4. **Assessment overview** — repository identifier, detected technologies/languages, health score.
5. **Why this score?** — score explanation, positive signals, limitations.
6. **Findings explorer** — one filtered finding expanded with evidence/recommendation.
7. **Priority risks** — P0/P1 items if the chosen real repository produces them; otherwise capture the actual priorities produced.
8. **Roadmap** — expanded phase and action showing effort, prerequisites, acceptance criteria, and automation safety.
9. **Blockers/warnings** — only if the real assessment returns them.
10. **Exports** — show actual download controls and, where practical, the downloaded report file.
11. **Mobile view** — real responsive layout on a narrow viewport.
12. **Health check** — optional terminal/API capture of `/api/v1/health` for technical credibility.

## Recommended video pacing

- 15–20 seconds: landing/input
- 20–30 seconds: analysis/loading
- 45–60 seconds: score/explainability
- 45–60 seconds: findings/risks
- 45–60 seconds: roadmap
- 15–30 seconds: export
- 20–30 seconds: security/trust closing

## Authenticity checklist

Before recording:

- Backend is running locally.
- Frontend is running locally.
- Selected repository is public and accessible.
- Internet/DNS access is verified.
- Results are generated during the recording or clearly identified as a previously captured authentic run.
- No fake fixture result is presented as a live repository result.
- Browser console contains no unresolved errors relevant to the demo.

## Backup capture

If live GitHub access fails during recording, use the deterministic local fixture/test workflow and explicitly label the screen or narration as a local deterministic fixture demonstration.
