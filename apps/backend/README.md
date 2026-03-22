# Backend (Litestar)

Python API service inside monorepo.

## Prerequisites

- Python 3.12+
- `uv`

## Setup

```bash
cd apps/backend
uv sync --dev
```

## Run locally

```bash
uv run alembic upgrade head
uv run litestar --app main:app run --host 0.0.0.0 --port 8000 -d
```

Health endpoint:

- `GET /health`

## Migrations

Create migration:

```bash
uv run alembic revision --autogenerate -m "message"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Apply migrations with mock demo data seed:

```bash
APP_MIGRATION_ALLOW_MOCK_DATA=true uv run alembic upgrade head
```

Rollback one migration:

```bash
uv run alembic downgrade -1
```

Mock data migration notes:

- Mock data is inserted only when `APP_MIGRATION_ALLOW_MOCK_DATA=true`.
- For downgrade of the mock-data migration, use the same env variable so seeded rows are removed.

## Quality checks

```bash
uv run ruff check .
uv run ruff format .
uv run mypy .
```

## Configuration

Preferred configuration source:

- environment variables `APP_*` (see `.env.example`)

Fallback configuration source:

- `.secrets.yaml` (example in `example.secrets.yaml`)

Telegram-only authentication requires:

- `APP_SECURITY__TELEGRAM__BOT_TOKEN`
- `APP_SECURITY__TELEGRAM__BOT_USERNAME`

Avatar uploads to MinIO require:

- `APP_OBJECT_STORAGE__ENDPOINT`
- `APP_OBJECT_STORAGE__ACCESS_KEY`
- `APP_OBJECT_STORAGE__SECRET_KEY`
- `APP_OBJECT_STORAGE__SECURE`
- `APP_OBJECT_STORAGE__BUCKET`
- `APP_OBJECT_STORAGE__PUBLIC_BASE_URL`
- `APP_OBJECT_STORAGE__PUBLIC_INCLUDE_BUCKET` (`true`/`false`, optional)
- `APP_OBJECT_STORAGE__MAX_UPLOAD_SIZE_MB`

## Organizer Ingest API

Public data import endpoint for organizers:

- `POST /api/public/organizer/import`
- auth header: `X-API-Key: <plain-token>`
- one request contains data for exactly one hackathon (`hackathon` object)

Write operations for hackathons/teams/results were moved to this endpoint.
Legacy write endpoints for `teams/events/ratings` are removed.
All imported hackathon data is marked verified automatically (`is_verify=true`).

Organizer tokens are stored in DB table `organizer_api_tokens` as SHA-256 hashes.
To create a token manually:

1. Generate token value.
2. Compute hash (example):
   ```bash
   printf '%s' 'YOUR_TOKEN' | shasum -a 256
   ```
3. Insert hash to DB:
   ```sql
   INSERT INTO organizer_api_tokens (name, token_hash, is_active, created_at, updated_at)
   VALUES ('organizer-name', '<sha256-hash>', true, NOW(), NOW());
   ```
