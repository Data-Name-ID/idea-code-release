---
name: frontend-vue-feature-flow
description: Implement and modify Vue features in apps/frontend with Vite and TypeScript while preserving routing conventions, environment contracts, and lint/typecheck gates. Use for UI changes, route changes, and frontend API integration tasks.
---

# Frontend Vue Feature Flow

Use this skill for all changes under `apps/frontend`.

## Workflow

1. Confirm route/component scope.
2. Confirm API contract assumptions.
3. Implement minimal UI and state changes.
4. Run frontend quality gates.
5. Produce concise change and risk notes.

## Implementation Rules

- Keep changes inside `apps/frontend/**` unless task explicitly requires cross-scope edits.
- Preserve `VITE_API_BASE_URL` as the API entry contract.
- Keep router changes explicit in `src/router/**`.
- Prefer typed API adapters over inline fetch calls spread across views.
- Avoid adding new state libraries unless explicitly requested.

## Quality Gates

Run from repo root:

```bash
yarn workspace frontend lint
yarn workspace frontend typecheck
```

## API Contract Changes

If backend contract is missing or incompatible:

1. Document required endpoint/env change.
2. Stop short of backend edits unless requested.
3. Hand off using `references/backend-contract-request.md`.
