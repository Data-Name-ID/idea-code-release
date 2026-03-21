# idea-code-release Monorepo

Monorepo for frontend and backend development with conventions optimized for team collaboration and Codex agents.

## Stack

- Frontend: Yarn 1, Vite, Vue 3, TypeScript, Vue Router
- Backend: Python 3.12, uv, Litestar, SQLAlchemy, Alembic
- Infra: Docker Compose, Postgres, Redis

## Repository layout

- `apps/frontend` - Vue app
- `apps/backend` - Litestar API
- `.codex/skills` - project Codex skills
- `.github/workflows` - CI pipelines

## Prerequisites

- Node.js 20+
- Yarn 1.22.22
- Python 3.12+
- `uv`
- Docker + Docker Compose

## Local development

Install frontend dependencies:

```bash
yarn install
```

Install backend dependencies:

```bash
cd apps/backend
uv sync --dev
```

Run services without Docker (two terminals):

```bash
yarn dev:frontend
yarn dev:backend
```

## Docker

Single production-style compose:

```bash
cp .env.example .env
docker compose up --build
```

For Telegram Login Widget on local development:

- keep `VITE_TELEGRAM_WIDGET_HOSTNAME=localhost`
- open frontend as `http://localhost:5173` (not `127.0.0.1`)
- set BotFather `/setdomain` to `localhost` (without protocol and port)

Default ports:

- Frontend prod: `5173`
- Backend: `8000`
- Postgres: `5432`
- Redis: `6379`

## Quality gates

```bash
yarn lint
yarn typecheck
```

## Environment

Frontend:

- copy `apps/frontend/.env.example` to `.env` if needed

Backend:

- primary source: environment variables with `APP_` prefix
- example: `apps/backend/.env.example`
- optional fallback file: `apps/backend/.secrets.yaml`
- Telegram auth requires `APP_SECURITY__TELEGRAM__BOT_TOKEN` and `APP_SECURITY__TELEGRAM__BOT_USERNAME`
