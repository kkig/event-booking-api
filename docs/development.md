# Development Guide

This guide covers environment setup, common development tasks, and local production verification.


## Project Configuration

- **Python compatibility:** `>=3.14,<3.15`, defined in `backend/pyproject.toml`.
    - **Development and CI:** Use uv-managed Python at the version pinned in `backend/.python-version`.
    - **Production:** Uses the Python interpreter supplied by the base image in `backend/Dockerfile`.
- **Python dependencies:** Locked in `backend/uv.lock`.
- **uv version:** Pinned to `0.12.23` in the Dockerfile and GitHub Actions. Using the same version locally is recommended for consistency.
- **PostgreSQL version:** Pinned in `compose.yml` and the GitHub Actions test workflow.
- **Environment configuration:** Copy `.env.example` to `.env` and configure the required values for your environment.

Using consistent tool versions across environments helps make development and CI behavior more predictable.


## Development Workflows

Choose either the Development Container or Local Development workflow.

The development environment uses the `event-booking-dev` Docker Compose project. The development database is exposed on host port `5433` to avoid conflicting with a locally installed PostgreSQL instance.

Running `scripts/bootstrap.sh` prepares the backend development environment by:
- Running `uv sync --frozen` to create or update `backend/.venv` and install the locked dependencies.
- Installing pre-commit if needed and registering Git hooks.

Infrastructure commands in the `Makefile` are intended to run from a host terminal with Docker Compose available. `make` is optional. You can run the equivalent Docker Compose commands directly.


### Development Container

The development environment runs the `web` service for Django and the `db` service for PostgreSQL.
The `web` service is configured to use uv-managed Python (`UV_PYTHON_PREFERENCE=managed` in `backend/Dockerfile`).

#### Required on host

- Docker Desktop (or Docker Engine with Docker Compose)
- Visual Studio Code
    - Dev Containers extension
- `make` (optional, for infrastructure commands)

#### Setup

1. Clone the repository and open it in VS Code.
2. Create your local environment file from the example.
    ```bash
    # Run in the repository root on host machine cli
    cp .env.example .env
    ```
3. Select **Reopen in Container** in VS Code.

    The development container image includes `uv`. The bootstrap script runs automatically after the container is created.

The development API is exposed at `http://localhost:8000`.

#### When to Rebuild the Development Container

The repository is bind-mounted into the development container at `/workspace`. Most file changes are therefore available immediately without rebuilding the container.

| Change            | Action needed                                |
| ------------------ | ------------------------------------------ |
| Python source code, tests, or documentation | No rebuild needed |
| `backend/pyproject.toml` or `backend/uv.lock` | Run `uv sync --frozen` from `backend/` to update dependencies |
| `backend/.python-version` | Install the selected Python version with `uv`, then run `uv sync` |
| `backend/Dockerfile`, Compose files, or `.devcontainer/` configuration | Rebuild the Dev Container |
| `.env` values passed to containers | Recreate the affected container to apply the updated environment |


### Local Development

In this workflow, Django runs on the host machine, while PostgreSQL runs in a Docker container. The Python environment and dependencies are managed by `uv`.

#### Required on host

- [uv (Python package manager)](https://docs.astral.sh/uv/getting-started/installation/)
    - The same version used in Dockerfile and GitHub Actions
- Docker Desktop (or Docker Engine with Docker Compose)
- `make` (optional, for infrastructure commands)

#### Setup

1. Clone the repository.
2. Create your local environment file from the example:
    ```bash
    # Run in the repository root
    cp .env.example .env
    ```
3. Bootstrap the development environment.
    ```bash
    # Run in the repository root
    scripts/bootstrap.sh
    ```
4. Start PostgreSQL container.
    ```bash
    # Run in the repository root
    make db-detach

    # Alternatively, without make command
    docker compose \
        -f compose.yml \
        -f compose.dev.yml \
        up -d db
    ```
5. Run database migrations.
   ```bash
   # Run in backend directory
   uv run python manage.py migrate
   ```
6. Start the Django development server.
    ```bash
    # Run in backend directory
    uv run python manage.py runserver
    ```

The API is exposed at `http://localhost:8000`.


## Common Infrastructure Commands

Run these commands from the **repository root**. The Makefile provides a consistent interface for operating the Docker Compose environments, independently of which editor you use.

### Development Environment

| Command            | Description                                |
| ------------------ | ------------------------------------------ |
| `make up`| Build and start development services in the foreground |
| `make up-detach`| Build and start development services in the background |
| `make down`| Stop and remove development containers |
| `make build`| Build development images |
| `make rebuild`| Rebuild development images without using the build cache |
| `make db`| Start the database service in the foreground |
| `make db-detach`| Start the database service in the background |
| `make db-down`| Stop the development database service |

Use `make up` when you want the application and database running in Docker. Use `make db-detach` when running Django directly on your machine and using Docker only for PostgreSQL.


## Local Production Verification

The repository includes a production-oriented Compose configuration for testing the production image locally. The production environment use the `event-booking-prod` Docker Compose project, with `web` and `db` containers. It can coexist with the development environment.

This configuration is intended for local verification and testing of the production container setup. It is **not a public deployment configuration**.

The production API is exposed at `http://localhost:8001`.


| Command            | Description                                |
| ------------------ | ------------------------------------------ |
| `make prod-build`| Build the production web image |
| `make prod-rebuild`| Rebuild the production web image without using the build cache |
| `make prod-migrate`| Run database migrations using the production image |
| `make prod-up`| Start the production verification services in the background |
| `make prod-down`| Stop and remove production verification containers |

Typical verification workflow:
```bash
make prod-build
make prod-migrate
make prod-up
```


## Pre-commit

Git hooks are installed automatically during environment setup using `scripts/bootstrap.sh`.

Run the following commands from the **repository root** to invoke the hooks manually:
```bash
# Run pre-commit hooks
uv run --project backend --frozen pre-commit run --all-files

# Run pre-push hooks
uv run --project backend --frozen pre-commit run --hook-stage pre-push --all-files
```


## Running Tests

Run the test suite from the `backend` directory:
```bash
uv run pytest
```

The suite includes tests for permissions, validation, booking cancellation, event capacity, and concurrent booking attempts.


## Backend Development Commands

Run the following commands from the `backend` directory.

| Command            | Description                                |
| ------------------ | ------------------------------------------ |
| `uv run ruff check .`| Check for linting issues                   |
| `uv run ruff check --fix .`| Fix automatically correctable lint issues               |
| `uv run ruff format .`| Auto-format code using style guidelines    |
| `uv run ruff format --diff .`| Preview formatting changes |
| `uvx codespell .`| Run spell checks                           |
