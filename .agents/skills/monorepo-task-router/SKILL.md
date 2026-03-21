---
name: monorepo-task-router
description: Route implementation tasks across this monorepo by ownership and risk. Use when a request touches multiple areas, has unclear scope boundaries, or needs a precise handoff between frontend, backend, and infra contributors.
---

# Monorepo Task Router

Use this skill to decide ownership, split work, and hand off tasks without scope drift.

## Triage

1. Map impacted files to owners.
2. Detect cross-scope dependencies early.
3. Define explicit in-scope and out-of-scope paths.
4. Pick the minimal set of owners needed.

Use this ownership map:

- `apps/frontend/**` -> frontend owner
- `apps/backend/**` -> backend owner
- `docker-compose.yml`, Dockerfiles, `.github/workflows/**`, root scripts -> infra owner

## Split Strategy

Prefer one owner when possible. Split only when one of these is true:

- API contract and UI integration both change.
- Infrastructure changes are required for runtime or CI.
- Migration work and feature work can be isolated safely.

When splitting, assign disjoint write scopes.

## Handoff Contract

When passing work, include all of the following:

- Goal and acceptance criteria.
- Exact in-scope paths.
- Exact out-of-scope paths.
- Commands required for verification.
- Known risks, assumptions, and rollback note.

Use `references/handoff-template.md` as the default handoff format.

## Conflict Rules

- Never change another owner’s area without explicit note in handoff.
- Never couple refactors with feature delivery in one handoff.
- Escalate when backward compatibility is unclear.
