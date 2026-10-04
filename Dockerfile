# Same shape as ai-circus-framework's services/*/Dockerfile: pinned uv, BuildKit uv
# cache, precompiled bytecode, root-owned code and a non-root runtime user.

# ── Builder stage: install all deps into a clean venv ─────────────────────────
FROM python:3.14-slim AS builder
# Pinned (not :latest) so builds are reproducible; bump deliberately.
COPY --from=ghcr.io/astral-sh/uv:0.12.13 /uv /uvx /bin/

WORKDIR /app

# Precompile bytecode at build time: a fresh container never has .pyc files on disk, so
# every start would otherwise recompile each imported module on first use.
# UV_LINK_MODE=copy because the uv cache is a mount.
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Layer 1: deps only (cached unless pyproject.toml / uv.lock change)
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv,id=uv-cache,sharing=locked \
    uv sync --frozen --no-dev --no-install-project

# Layer 2: install the project package itself
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv,id=uv-cache,sharing=locked \
    uv sync --frozen --no-dev

# ── Runtime stage: copy only the installed venv + source ──────────────────────
# No uv here: the venv is complete, and every extra binary is extra attack surface.
FROM python:3.14-slim AS runtime
WORKDIR /app

# The code/venv below stay root-owned (read-only to the app): only the home
# directory (caches) is writable by the non-root user. The base image's pip is
# removed: the app never uses it, and its vendored urllib3/msgpack/setuptools are
# what image scanners (Trivy) flag as HIGH CVEs. Debian security fixes released
# after the base image was published are applied too.
RUN apt-get update \
    && apt-get upgrade --yes --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 --shell /usr/sbin/nologin app \
    && python -m pip uninstall --yes --quiet pip

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src   /app/src
COPY --from=builder /app/pyproject.toml /app/pyproject.toml
COPY --from=builder /app/settings.yaml  /app/settings.yaml

ENV PATH="/app/.venv/bin:$PATH"
# PYTHONUNBUFFERED: logs reach `docker logs` immediately, and aren't lost on a crash.
# MALLOC_ARENA_MAX=2: caps glibc's per-thread malloc arenas (lower steady-state RSS).
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 MALLOC_ARENA_MAX=2

USER app

# Entry point
CMD ["python", "-m", "ai_circus.app"]
