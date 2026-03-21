# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hackathon/event platform ("Пицца хаб") with Telegram auth. Monorepo with a Vue 3 frontend and a Python (Litestar) backend.

## Commands

```bash
# Frontend
yarn dev:frontend                    # Dev server on :5173
yarn lint:frontend                   # ESLint (zero warnings enforced)
yarn typecheck:frontend              # vue-tsc --noEmit
cd apps/frontend && yarn build       # Type-check + Vite build

# Backend
yarn dev:backend                     # Litestar on :8000 (requires uv)
yarn lint:backend                    # ruff check
yarn typecheck:backend               # mypy

# Docker (full stack with Postgres + Redis)
yarn docker:up                       # docker compose up --build
yarn docker:down
```

No test runner is configured. Validation is lint + typecheck + build.

## Frontend Architecture

**Stack:** Vue 3 + TypeScript + Vite + SCSS + vue-router. Package manager is Yarn 1 (workspaces).

### Feature-Sliced Design (FSD)

All frontend code lives under `apps/frontend/src/` and follows FSD layers:

- **`shared/`** — Design tokens, API client, auth, router, types, composables, utilities. No business logic.
- **`entities/`** — Domain API modules (`user/api.ts`, `team/api.ts`, `event/api.ts`, `role/api.ts`, `skill/api.ts`). Thin wrappers around `apiFetch`.
- **`widgets/`** — Reusable UI blocks: `ActivityFeed`, `TeamsCard`, `SpecializationCard`, `UserProfileCard`. Each has `ui/` and optionally `model/types.ts`.
- **`pages/`** — Route-level components. Each has `ui/`, optionally `model/types.ts`, and an `index.ts` barrel.

**Path aliases** (configured in both `vite.config.ts` and `tsconfig.app.json`):
`@shared`, `@entities`, `@widgets`, `@features`, `@pages`, `@app`

### SCSS System

`_index.scss` is auto-injected into every Vue component via Vite's `css.preprocessorOptions.scss.additionalData`. This means **all variables, mixins, and breakpoints are available without imports** in `<style scoped lang="scss">` blocks.

Key files:
- `shared/styles/_variables.scss` — Color tokens (`$color-*`), radii (`$radius-*`), typography, transitions
- `shared/styles/_mixins.scss` — Layout mixins (`page-root`, `sticky-header`, `back-button`, `card-interactive`, `skeleton-shimmer`, `flex-center`, `flex-between`, `flex-column`, `text-ellipsis`)
- `shared/styles/_breakpoints.scss` — Responsive breakpoint mixins

**Important:** `_mixins.scss` must `@use 'variables' as *;` at the top because Vite's `additionalData` injection does not apply inside other SCSS partials.

### Mock System

Set `VITE_USE_MOCKS=true` to run the frontend without a backend. Mocks intercept at the `apiFetch` level (`shared/api/client.ts`) — the mock handler (`shared/mocks/handler.ts`) pattern-matches API paths and returns fixture data from `shared/mocks/data.ts`.

### Key Patterns

- **Types** go in `model/types.ts` within the owning page or widget, not inline in `.vue` files. Shared API types live in `shared/types/api.ts`.
- **Composables** for shared data-fetching logic (e.g., `shared/composables/useUserActivity.ts` used by both ProfilePage and UserPage).
- **Shared utilities** in `shared/lib/format.ts` (`formatDateLong`, `formatDateShort`, `initials`, `ratingStatusLabel`).
- All components use `<script setup lang="ts">` with composition API.
- Router guard in `shared/router/index.ts` handles auth: `requiresAuth` redirects to `/auth`, `guestOnly` redirects to `/profile`.

## Backend Architecture

**Stack:** Python + Litestar + SQLAlchemy + Alembic + PostgreSQL. Uses `uv` as package manager.

- Entry point: `apps/backend/main.py` — Litestar app with JWT cookie auth
- Domain modules: `auth/`, `users/`, `events/`, `roles/`, `skills/` — each with `models.py`, `schemas.py`, `views.py`, `urls.py`, `accessor.py`
- Config: `core/config.py`, DB: `core/db.py`, Migrations: `core/models/migrations/`
- Auth: Telegram Login Widget + JWT cookies. Dev auth endpoint available when `APP_SECURITY__DEV_AUTH_BY_TG_ID_ENABLED=true`.
- API docs at `/docs` (Scalar UI)

## Environment Variables

Frontend (prefixed `VITE_`):
- `VITE_API_BASE_URL` — Backend URL (default: `http://localhost:8000`)
- `VITE_USE_MOCKS` — `"true"` to enable client-side mocks
- `VITE_TELEGRAM_WIDGET_HOSTNAME` — Expected hostname for Telegram widget domain validation

Backend (prefixed `APP_`): see `docker-compose.yml` for full list. Key ones:
- `APP_DB__*` — Postgres connection
- `APP_SECURITY__JWT__TOKEN_SECRET` — JWT signing secret
- `APP_SECURITY__TELEGRAM__BOT_TOKEN` / `BOT_USERNAME` — Telegram auth config
