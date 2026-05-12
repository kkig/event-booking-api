# ------------------------------------------------------------
# Base Stage: Installs UV and Dependencies
# ------------------------------------------------------------
FROM python:3.13-slim AS base

# Avoid writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Forces stdout/stderr to be unbuffered. For logging in Docker.
ENV PYTHONUNBUFFERED=1

# Install packages directly to the system Python. No venv needed.
# ENV UV_SYSTEM_PYTHON=1

# Use cache mounts to improve performance of uv installs.
ENV UV_LINK_MODE=copy

# Disable uv's automatic downloading of Python versions. We rely on the base image's Python.
ENV UV_PYTHON_DOWNLOADS=0


# Install required system dependencies.
# Clean up apt lists to reduce image size.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory.
WORKDIR /code

# Install uv from the official image.
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /bin/uv

# Copy only the dependency files first to leverage Docker caching.
COPY pyproject.toml uv.lock ./


# ------------------------------------------------------------
# Development / Testing Stage
# ------------------------------------------------------------
FROM base AS development

# Set uv to use virtual environments in /opt/.venv.
# This keeps dependencies isolated and allows for faster installs in development.
ENV UV_PROJECT_ENVIRONMENT=/opt/.venv

# Activate the virtual environment to use installed dependencies.
ENV PATH="/opt/.venv/bin:$PATH"

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

# Ensure commands complile to bytecode for faster startup in production. (Optional)
ENV UV_COMPILE_BYTECODE=1

# Install ONLY production dependencies (--no-dev).
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy application source code.
COPY ./backend /code

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
