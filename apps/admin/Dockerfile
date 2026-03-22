FROM python:3.12-slim AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /workspace
ENV PATH="/workspace/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM base AS runtime
COPY . .

FROM base AS dev
RUN uv sync --frozen --dev
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8010"]

FROM runtime AS migrate
CMD ["python", "manage.py", "migrate", "--noinput"]

FROM runtime AS prod-admin
RUN python manage.py collectstatic --noinput
CMD ["sh", "-c", "python manage.py ensure_superuser && python manage.py runserver 0.0.0.0:8010"]
