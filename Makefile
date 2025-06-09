# Docker service name (as defined in docker-compose.yml)
WEB=web

# -----------------------------
# Django Management Commands
# -----------------------------

# Apply all database migrations
migrate:
	docker-compose exec $(WEB) python manage.py migrate

# Create new migration files based on model changes
migrations:
	docker-compose exec $(WEB) python manage.py makemigrations

# Create a Django superuser (interactive)
createsuperuser:
	docker-compose exec $(WEB) python manage.py createsuperuser

# Open the Django shell inside the container
shell:
	docker-compose exec $(WEB) python manage.py shell


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
	docker-compose exec $(WEB) pytest

# Lint code using flake8, isort, and black (check-only)
lint:
	flake8 .
	isort --check-only .
	black --check .

# Format code using black, flake8, and isort
format:
	black .
	flake8 .
	isort .
	codespell .
