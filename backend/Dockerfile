# ------------------------------------------------------------
# Base Stage: Installs UV and Dependencies
# ------------------------------------------------------------
FROM python:3.14-slim AS base

# Avoid writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Forces stdout/stderr to be unbuffered. For logging in Docker.
ENV PYTHONUNBUFFERED=1

# Use cache mounts to improve performance of uv installs.
ENV UV_LINK_MODE=copy


# Install required system dependencies.
# Clean up apt lists to reduce image size.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory.
WORKDIR /workspace/backend

# Install uv from the official image.
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /bin/uv

# Copy only the dependency files first to leverage Docker caching.
COPY ./backend/pyproject.toml ./backend/uv.lock ./


# ------------------------------------------------------------
# Development / Testing Stage
# ------------------------------------------------------------
FROM base AS development

ENV UV_PYTHON_PREFERENCE=managed

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Ensure uv global tools are automatically available on the PATH
ENV PATH="/root/.local/bin:${PATH}"

# Install project dependencies.
# This stays cached unless pyproject.toml or uv.lock changes.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# In dev, we don't COPY the code because we use volumes in compose to sync the code.
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]


# ------------------------------------------------------------
# Production Stage
# ------------------------------------------------------------
FROM base AS production

# Ensure commands compile to bytecode for faster startup in production. (Optional)
ENV UV_COMPILE_BYTECODE=1

ENV UV_PYTHON_PREFERENCE=system

# Install ONLY production dependencies (--no-dev).
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy application source code.
COPY . .

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
