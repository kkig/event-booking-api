# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

# Docker service name (as defined in docker-compose.yml)
WEB=web

# Tells Make to always run the specified targes,
# even if folders/files with the same name exist in the root directory.
.PHONY: migrate migrations createsuperuser shell up up-detach down build rebuild test lint lint-fix format format-diff spellcheck


# -----------------------------------------------------------------------------
# Django Management Commands
# -----------------------------------------------------------------------------

# Apply all database migrations
migrate:
	docker compose run --rm $(WEB) uv run manage.py migrate

# Create new migration files based on model changes
migrations:
	docker compose run --rm $(WEB) uv run manage.py makemigrations

# Create a Django superuser (interactive)
createsuperuser:
	docker compose exec $(WEB) uv run manage.py createsuperuser

# Open the Django shell inside the container
shell:
	docker compose exec $(WEB) uv run manage.py shell


# -----------------------------------------------------------------------------
# Docker Compose Commands
# -----------------------------------------------------------------------------

# Start all services (foreground)
up:
	docker compose up

# Start all services (detached mode)
up-detach:
	docker compose up -d

# Stop all services and remove containers
down:
	docker compose down

# Build all containers
build:
	docker compose build

# Rebuild containers from scratch (no cache)
rebuild:
	docker compose build --no-cache


# -----------------------------------------------------------------------------
# Testing & Code Quality (Run locally for speed)
# -----------------------------------------------------------------------------

# Run all tests inside the container
test:
	docker compose run --rm -T $(WEB) pytest --color=yes

# Run ruff to check for linting issues locally
lint:
	cd backend && uv run ruff check .

# Automatically fix fixable linting issues
lint-fix:
	cd backend && uv run ruff check --fix .

# Format code according to project style guidelines
format:
	cd backend && uv run ruff format .

format-diff:
	cd backend && uv run ruff format --diff .

# Run spellcheck on codebase
spellcheck:
	uvx codespell .
