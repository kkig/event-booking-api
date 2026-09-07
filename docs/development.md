# Development Guide

This guide covers setting up and developing the project.


## Development Workflows

### Development Container

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

### Local Development

#### Prerequisites

- Python 3.14
- [uv (Python package manager)](https://docs.astral.sh/uv/getting-started/installation/)
- Docker
- `make` (optional, for infrastructure commands)

#### Setup

1. Bootstrap the development environment:
    ```bash
    scripts/bootstrap.sh
    ```

2. Run database migrations:
   ```bash
   cd backend
   uv run manage.py migrate
   ```


## Pre-commit

Git hooks are installed automatically during environment setup.

To run the hooks manually:

```bash
# Run pre-commit hooks
uv run pre-commit run --all-files

# Run pre-push hooks
uv run pre-commit run --hook-stage pre-push --all-files
```


## Running Tests

Run the test suite from the `backend` directory:
```bash
uv run pytest
```
