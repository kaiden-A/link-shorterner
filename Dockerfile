# syntax=docker/dockerfile:1
FROM python:3.14-slim

LABEL org.opencontainers.image.source="https://github.com/kaiden-A/link-shorterner"
LABEL org.opencontainers.image.description="Link Shortener API"
LABEL org.opencontainers.image.version="0.1.0"

# ── Python runtime tuning ──────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ── Install Python dependencies (layer-cached) ─────────────────────────
# Removed apt-get libpq5 since psycopg[binary] bundles its own shared libs.
COPY pyproject.toml .
RUN pip install --no-cache-dir \
        "alembic>=1.18.5" \
        "bcrypt>=5.0.0" \
        "fastapi>=0.139.0" \
        "psycopg[binary]>=3.3.4" \
        "pydantic-settings>=2.14.2" \
        "pydantic[email]>=2.13.4" \
        "pyjwt>=2.13.0" \
        "python-dotenv>=1.2.2" \
        "sqlalchemy>=2.0.51" \
        "uvicorn[standard]>=0.51.0" && \
    pip check

# ── Application source ─────────────────────────────────────────────────
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# ── Non‑root user (Cloud Run security best practice) ───────────────────
RUN addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 --gid 1001 appuser && \
    chown -R appuser:appuser /app

USER appuser

# ── Port ───────────────────────────────────────────────────────────────
# Cloud Run injects $PORT; 8080 is the default.
EXPOSE 8080

# ── Start server ───────────────────────────────────────────────────────
# Using 'exec' inside the shell form ensures Uvicorn becomes PID 1.
# This allows Cloud Run to gracefully shut down the container (SIGTERM).
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}