# LegacyLens — Hackathon Submission Checklist

## Submission package (IBM Bob 2.0 / lablab.ai)

- [x] Authentic screenshots captured into `docs/screenshots/` (`01-landing.png` … `08-exports.png`, captured from the running app analyzing `pallets/flask`).
- [ ] Demo video recorded, under 3 minutes.
- [ ] `bob_sessions/` directory with the IBM Bob session exports.
- [ ] 500-word statement on how IBM Bob was used during development.
- [ ] 500-word problem & solution statement.
- [ ] Slide deck exported to PDF.
- [ ] Public GitHub repository URL created and added here and to the submission form.
- [ ] lablab.ai submission form completed.

## Technical

- [x] Backend starts successfully.
- [x] Frontend starts successfully.
- [x] `GET /api/v1/health` returns the expected status.
- [x] `POST /api/v1/analyses` works with a reachable public GitHub repository.
- [x] Canonical JSON export works.
- [x] Canonical Markdown export works.
- [x] Canonical HTML export works.
- [x] Backend regression suite passes (31 tests).
- [x] Python compilation passes (`python -m compileall -q backend/app`).
- [ ] Frontend `npm install`/`npm ci` succeeds in the demo environment.
- [ ] Frontend lint succeeds (`npm run lint` not run in this environment).
- [x] TypeScript validation succeeds (`npx tsc --noEmit`, exit 0).
- [x] Next.js production build succeeds (all routes static).
- [x] Environment variables are documented.
- [x] No secrets are committed (`frontend/.env.local` is gitignored and contains only the API base URL).
- [x] README is current.

## Demo

- [x] Public demo repository selected (`https://github.com/pallets/flask`).
- [x] Internet/DNS access verified (live analysis completed).
- [x] Backup deterministic fixture prepared (backend test fixtures).
- [x] Authentic screenshots captured.
- [ ] Demo video recorded.
- [ ] 3–5 minute demo script rehearsed (`docs/HACKATHON_DEMO_SCRIPT.md` and `docs/DEMO_RUNBOOK.md` exist).
- [x] Browser mobile view checked (375 px harness pass, no horizontal overflow).
- [ ] Failure fallback prepared.

## Security

- [x] No credentials are committed.
- [x] `.env` is excluded.
- [x] No unsafe HTML injection is present (no `dangerouslySetInnerHTML`; exports escaped).
- [x] Repository code is not executed.
- [x] Archive extraction limits are enabled.
- [x] GitHub URL validation is active.
- [x] Redirects outside the allowlist (`github.com`, `codeload.github.com`, `objects.githubusercontent.com`) are rejected.
- [x] Traversal/link protections are active.
- [x] Errors are sanitized.
- [x] Export filenames are fixed/safe.

## Submission metadata

- [x] Project name: LegacyLens
- [x] Project description finalized (README pitch + one-liner).
- [x] Team members finalized (AWAIS-EKREMAH: Awais Jabbar, Muhammad Ekremah).
- [ ] Repository URL added.
- [ ] Demo URL added, if available.
- [ ] Video URL added, if available.
- [x] Screenshots added.
- [x] Architecture diagram added (README ASCII pipeline diagram).
- [x] README finalized.
- [x] License decision finalized (MIT).
- [x] Known limitations reviewed.
