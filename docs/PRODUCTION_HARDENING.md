# Production Hardening

## Scope

This phase hardens the existing architecture without adding authentication, queues, microservices, or a new persistence layer.

## Controls reviewed

### Repository ingestion

- HTTPS GitHub allowlist
- Credential/custom-port/query/fragment rejection
- No-redirect archive fetch
- Download-size limit
- ZIP/TAR traversal checks
- Absolute/drive/path-length checks
- Symlink/hardlink rejection
- File-count and extraction-size limits
- Temporary workspace cleanup
- No repository execution or dependency installation

### API

- Request body size limit
- Basic in-process rate limiting
- Restricted CORS
- Security response headers
- Generic exception responses
- Request IDs
- No user-controlled export response filenames

### Frontend

- No `dangerouslySetInnerHTML`
- No repository-derived HTML execution
- No client-side server secrets
- Static/known internal navigation only
- Safe download filename generation
- HTML exports are downloaded, never injected

### Reporting

- Stable JSON/Markdown/HTML serialization
- HTML escaping
- Self-contained HTML without external resources
- Fixed Content-Disposition filenames
- Invalid report input returns validation errors rather than stack traces

## Residual risks and limitations

- In-process rate limiting is not a distributed production control.
- Live GitHub ingestion depends on outbound DNS/network access.
- Static analysis cannot prove runtime security or absence of vulnerabilities.
- Reports are not persisted in the current architecture.
- Frontend build and browser QA remain environment-dependent in the current constrained workspace.

The project should be described as **security-conscious and hardened for the hackathon/demo context**, not as absolutely secure or production-proof.
