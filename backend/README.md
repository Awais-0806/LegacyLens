# LegacyLens Backend

FastAPI backend foundation.

## Local

From `backend/`:

```bash
python -m pytest
python -m uvicorn app.main:app --reload --port 8000
```

The development configuration defaults to SQLite. Production should set `APP_ENV=production` and a PostgreSQL `DATABASE_URL`.
