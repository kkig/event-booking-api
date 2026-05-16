# Docker service name (as defined in docker-compose.yml)
WEB=web

# -----------------------------
# Django Management Commands
# -----------------------------

# Apply all database migrations
migrate:
	docker-compose run --rm $(WEB) uv run manage.py migrate

# Create new migration files based on model changes
migrations:
	docker-compose run --rm $(WEB) uv run manage.py makemigrations

# Create a Django superuser (interactive)
createsuperuser:
	docker-compose exec $(WEB) uv run manage.py createsuperuser

# Open the Django shell inside the container
shell:
	docker-compose exec $(WEB) uv run manage.py shell


# -----------------------------
# Docker Compose Commands
# -----------------------------

# Start all services (foreground)
up:
	docker-compose up

# Start all services (detached mode)
up-d:
	docker-compose up -d

# Stop all services and remove containers
down:
	docker-compose down

# Build all containers
build:
	docker-compose -f docker-compose.yml build

# Rebuild containers from scratch (no cache)
rebuild:
	docker-compose build --no-cache


# -----------------------------
# Testing & Code Quality
# -----------------------------

# Run all tests using pytest
test:
	docker-compose run --rm $(WEB) pytest

# Run ruff to check for linting issues locally
ruff:
	cd backend && uv run ruff check .

ruff-fix:
	cd backend && uv run ruff check --fix .

ruff-format:
	cd backend && uv run ruff format .

# Lint code using flake8, isort, and black (check-only)
lint:
	docker-compose run --rm $(WEB) flake8 .
	docker-compose run --rm $(WEB) isort --check-only .
	docker-compose run --rm $(WEB) black --check .

# Format code using black, flake8, and isort
format:
	docker-compose run --rm $(WEB) black .
	docker-compose run --rm $(WEB) flake8 .
	docker-compose run --rm $(WEB) isort .
	docker-compose run --rm $(WEB) codespell .
