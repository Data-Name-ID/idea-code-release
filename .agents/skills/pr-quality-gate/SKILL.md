---
name: pr-quality-gate
description: Run pre-PR quality checks and produce merge-ready summaries for this monorepo. Use when preparing a branch for review, validating agent output, or doing a final regression and risk pass.
---

# PR Quality Gate

Use this skill before opening or approving a PR.

## Required Checks

From repo root:

```bash
yarn lint
yarn typecheck
```

If backend migrations changed:

```bash
cd apps/backend
uv run alembic upgrade head
uv run alembic downgrade -1
```

## Review Pass

1. Validate scope matches task intent.
2. Identify regressions and contract changes.
3. Confirm no hidden infra/runtime side effects.
4. Confirm documentation reflects behavior changes.

## PR Output Format

Provide:

- Change summary by subsystem.
- Executed checks and outcomes.
- Risks and mitigations.
- Follow-up tasks intentionally deferred.

Use `references/pr-template.md` for consistent output.
