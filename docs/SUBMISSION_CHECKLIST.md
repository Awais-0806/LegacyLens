# LegacyLens — Hackathon Submission Checklist

## Technical

- [ ] Backend starts successfully.
- [ ] Frontend starts successfully.
- [ ] `GET /api/v1/health` returns the expected status.
- [ ] `POST /api/v1/analyses` works with a reachable public GitHub repository.
- [ ] Canonical JSON export works.
- [ ] Canonical Markdown export works.
- [ ] Canonical HTML export works.
- [ ] Backend regression suite passes.
- [ ] Python compilation passes.
- [ ] Frontend `npm install`/`npm ci` succeeds in the demo environment.
- [ ] Frontend lint succeeds.
- [ ] TypeScript validation succeeds.
- [ ] Next.js production build succeeds.
- [ ] Environment variables are documented.
- [ ] No secrets are committed.
- [ ] README is current.

## Demo

- [ ] Public demo repository selected.
- [ ] Internet/DNS access verified.
- [ ] Backup deterministic fixture prepared.
- [ ] Authentic screenshots captured.
- [ ] Demo video recorded.
- [ ] 3–5 minute demo script rehearsed.
- [ ] Browser mobile view checked.
- [ ] Failure fallback prepared.

## Security

- [ ] No credentials are committed.
- [ ] `.env` is excluded.
- [ ] No unsafe HTML injection is present.
- [ ] Repository code is not executed.
- [ ] Archive extraction limits are enabled.
- [ ] GitHub URL validation is active.
- [ ] Redirects are rejected.
- [ ] Traversal/link protections are active.
- [ ] Errors are sanitized.
- [ ] Export filenames are fixed/safe.

## Submission metadata

- [ ] Project name: LegacyLens
- [ ] Project description finalized.
- [ ] Team members finalized.
- [ ] Repository URL added.
- [ ] Demo URL added, if available.
- [ ] Video URL added, if available.
- [ ] Screenshots added.
- [ ] Architecture diagram added.
- [ ] README finalized.
- [ ] License decision finalized.
- [ ] Known limitations reviewed.
