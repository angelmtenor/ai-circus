FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY . /app

# Install dependencies
RUN uv sync --frozen --no-cache

# Entry point using the new app.py
CMD ["uv", "run", "python", "-m", "ai_circus.app"]
