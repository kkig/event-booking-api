# Development Guide

This is guide for setting up and developing in your environment.


## Development workflows

### Option A: Development Container

#### Prerequisites

- Docker Desktop (or Docker Engine with Docker Compose)
- Visual Studio Code
- Dev Containers extension

#### Setup

1. Open the repository in VS Code.

2. Select **Reopen in Container**.

The development container automatically:

- Installs Python dependencies using `uv`
- Creates the virtual environment in `backend/.venv`
- Installs git pre-commit hooks
- Configures the backend development environment

### Option B: Local Development

#### Prerequisites

- Python 3.14
- [uv (Python package manager)](https://docs.astral.sh/uv/getting-started/installation/)
- Docker
- make (optional, for infrastructure commands)

#### Setup

1. Bootstrap development environment:
    ```bash
    scripts/bootstrap.sh
    ```

2. Run database migrations:
   ```bash
   cd backend
   uv run manage.py migrate
   ```

## Pre-commit

Installing the hooks configures Git to automatically run formatting and validation before commits and pushes.

**How to test hooks:**
```bash
# Test pre-commit hooks
uv run pre-commit run --all-files

# Test pre-push hooks
uv run pre-commit run --hook-stage pre-push --all-files
```

## Running tests

From `backend` directory:
```bash
uv run pytest
```

## Backend Development Commands

Run the following commands from the `backend` directory.

| Command            | Description                                |
| ------------------ | ------------------------------------------ |
| `uv run ruff check .`| Check for linting issues                   |
| `uv run ruff check --fix .`| Check and fix fixable issues               |
| `uv run ruff format .`| Auto-format code using style guidelines    |
| `uv run ruff format --diff .`| See how the formatted code would look like |
| `uvx codespell .`| Run spell checks                           |
