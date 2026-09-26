# Frontend Assessment Dashboard

Phase 8 integrates the Next.js/React frontend with `POST /api/v1/analyses` and renders the real assessment response.

## Implemented
- Public GitHub URL validation and API submission
- Safe loading stages (presented as general processing stages, not live telemetry)
- Repository overview and static-analysis disclaimer
- Overall score ring, category score cards, weights and explanations
- Explainability signals and limitations
- Searchable/severity-filterable specialist findings with expandable evidence
- Prioritized risks and manual-review indicators
- Expandable roadmap phases/actions, quick-win data through canonical roadmap actions, blockers and acceptance criteria
- Client-side downloads for canonical JSON and safe Markdown/HTML report representations
- Empty, error, no-result, and optional-field-safe states
- Responsive CSS, semantic headings, labels, focusable controls, text-based status badges

## Security
No repository HTML is injected, no `dangerouslySetInnerHTML` is used, and downloaded HTML is never rendered in the app. The frontend does not contain API keys or execute repository content.

## Known limitations
- Backend does not expose live progress events, so loading stages are illustrative.
- The current backend response exposes the structured report, not serialized Markdown/HTML strings; the UI downloads faithful client-side representations from returned report data.
- Browser-level testing and frontend dependency installation/build depend on network/package availability.
