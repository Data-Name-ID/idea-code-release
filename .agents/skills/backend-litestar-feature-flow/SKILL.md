---
name: backend-litestar-feature-flow
description: Implement backend features in apps/backend using Litestar, SQLAlchemy, and Alembic with safe migration and contract discipline. Use for endpoint changes, schema changes, authentication updates, and backend configuration updates.
---

# Backend Litestar Feature Flow

Use this skill for backend work in `apps/backend`.

## Workflow

1. Identify API/domain/model impact.
2. Define schema and migration impact.
3. Implement handler/domain/accessor changes.
4. Apply migration safety checks.
5. Run backend quality gates.

## Implementation Rules

- Keep endpoint logic thin and domain logic in domain/accessor layers.
- For schema changes, always include migration intent and rollback note.
- Preserve `/health` and docs availability.
- Keep auth exclusions explicit when adding public endpoints.
- Preserve config contract: `APP_*` env vars and `.secrets.yaml` fallback.

## Migration Safety

When changing models:

- Add or update Alembic migration.
- Verify upgrade path and single-step downgrade.
- Call out destructive operations explicitly.

## Quality Gates

Run in `apps/backend`:

```bash
uv run ruff check .
uv run mypy .
```

Use `references/migration-checklist.md` before handoff.
