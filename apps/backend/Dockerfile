FROM python:3.12-alpine AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /workspace
ENV PATH="/workspace/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM base AS runtime
COPY . .

FROM base AS dev
RUN uv sync --frozen --dev
COPY . .
CMD ["litestar", "--app", "main:app", "run", "--host", "0.0.0.0", "--port", "8000", "-d"]

FROM runtime AS migrate
ENTRYPOINT ["alembic", "upgrade", "head"]

FROM runtime AS prod-api
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
