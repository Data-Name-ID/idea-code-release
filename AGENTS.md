# AGENTS Operating Guide

This document defines how human developers and Codex agents collaborate in this repository.

## Workflow Model

- Use trunk-based development.
- Keep branches short-lived (`< 2 days` preferred).
- Rebase on `main` before opening/merging PR.
- Merge only when CI is green.

## Roles and Ownership

- `frontend-agent`
  - Owns: `apps/frontend/**`
  - Owns frontend lint/typecheck fixes.
  - Must not change backend contracts without explicit coordination.
- `backend-agent`
  - Owns: `apps/backend/**`
  - Owns DB migrations and API behavior.
  - Must provide migration safety notes for schema changes.
- `infra-agent`
  - Owns: `docker-compose.yml`, Dockerfiles, `.github/workflows/**`, root automation.
  - Must verify compose configuration remains valid after infra changes.
- `reviewer-agent`
  - Owns quality gate review, regression risk checks, release notes.
  - Cannot approve changes without reproducible verification commands.

## Task Intake Template

Every implementation task must start with this minimum contract:

- Goal and expected outcome.
- In-scope paths.
- Out-of-scope paths.
- Acceptance checks.
- Risks and rollback strategy.

## Handoff Protocol

When handing work to another agent/human, include:

- What changed.
- What remains.
- Exact commands run.
- Open risks and assumptions.
- If migrations were added, include upgrade/downgrade commands.

## PR Checklist

Before opening PR, run:

```bash
yarn lint
yarn typecheck
```

For backend DB changes, additionally run:

```bash
cd apps/backend
uv run alembic upgrade head
uv run alembic downgrade -1
```

PR description must include:

- Scope summary (frontend/backend/infra).
- Contract changes (env vars, endpoints, compose services, scripts).
- Verification evidence (commands and outcome).
- Follow-up tasks if intentionally deferred.

## Change Boundaries

- Do not mix unrelated frontend and backend refactors in one PR.
- Separate infra-only changes into dedicated commits/PR when practical.
- Prefer additive migrations; destructive changes require explicit rollback plan.

## Codex-Specific Rules

- Prefer non-destructive commands.
- Do not rewrite or drop migrations already shared with team without approval.
- Keep edits inside owned scope unless task explicitly requires cross-scope changes.
- If a task requires cross-scope edits, call out impacted owners in handoff notes.
- Avoid hidden assumptions: document defaults in code comments or README when behavior is implicit.
- For backend data writes, prefer SQLAlchemy Core statements (`insert`, `update`, `delete`) instead of session ORM mutation flow (`add`, `flush`, `refresh`, `get`).
- Minimize DB round-trips: when possible, combine logic into a single SQL statement (CTE, `returning`, `on_conflict_*`, bulk operations) instead of multiple sequential queries.
- Avoid `N+1` query patterns; use explicit eager loading (`selectinload`/`joinedload`) or set-based queries/joins and validate list endpoints for query count growth.
- Prefer typed structures (e.g., `Struct`/domain objects) over raw `dict` at service and accessor boundaries; keep `dict` only where required by external libraries/SQLAlchemy payload APIs.

## Escalation

Escalate to maintainer when:

- API contract must change in a backward-incompatible way.
- Migration requires data backfill/destructive operations.
- Compose changes affect production runtime behavior.
- CI baseline must be expanded beyond lint/typecheck.
