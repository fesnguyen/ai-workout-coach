FROM python:3.12-slim

# Install the uv binary without adding an extra build dependency.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Don't generate .pyc files inside the container.
ENV PYTHONDONTWRITEBYTECODE=1

# Flush logs immediately instead of buffering stdout/stderr.
ENV PYTHONUNBUFFERED=1

# Copy files instead of hard-linking to avoid Docker filesystem issues.
ENV UV_LINK_MODE=copy

WORKDIR /workspace

# Install dependencies separately to maximize Docker layer caching.
COPY pyproject.toml uv.lock ./

RUN uv sync \
    --frozen \
    --no-dev \
    --no-install-project

# Copy project after dependencies so source changes don't invalidate the cache.
COPY . .

RUN uv sync \
    --frozen \
    --no-dev

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]