# ── Builder stage: install all deps into a clean venv ─────────────────────────
FROM python:3.14-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Layer 1: deps only (cached unless pyproject.toml / uv.lock change)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-dev --no-install-project

# Layer 2: install the project package itself
COPY . /app
RUN uv sync --frozen --no-cache --no-dev

# ── Runtime stage: copy only the installed venv + source ──────────────────────
FROM python:3.14-slim AS runtime

WORKDIR /app

# Copy uv binary (needed to run `uv run`)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy the pre-built venv and source from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src   /app/src
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

ENV PATH="/app/.venv/bin:$PATH"

# Entry point
CMD ["python", "-m", "ai_circus.app"]
