# Admin (Django + Unfold)

Standalone moderation/admin console for the existing Litestar backend data.

## Prerequisites

- Python 3.12+
- `uv`
- Access to the same Postgres DB used by `apps/backend`

## Setup

```bash
cd apps/admin
uv sync --dev
```

## Run locally

Ensure backend schema is up to date first:

```bash
cd apps/backend
uv run alembic upgrade head
```

Then run admin service:

```bash
uv run python manage.py migrate --noinput
uv run python manage.py ensure_superuser
uv run python manage.py runserver 0.0.0.0:8010
```

Admin URL:

- `http://localhost:8010/admin/`

## Environment

Database connection is read from `APP_DB__*` env vars:

- `APP_DB__USER`
- `APP_DB__PASSWORD`
- `APP_DB__HOST`
- `APP_DB__PORT`
- `APP_DB__NAME`

Django/admin settings:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS` (comma-separated)
- `DJANGO_CSRF_TRUSTED_ORIGINS` (comma-separated)
- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_EMAIL`
- `DJANGO_SUPERUSER_PASSWORD`
