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

Rollback one migration:

```bash
uv run alembic downgrade -1
```

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
