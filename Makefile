WEB=web

# Run management commands
migrate:
	docker-compose exec $(WEB) python manage.py migrate

makemigrations:
	docker-compose exec $(WEB) python manage.py makemigrations

createsuperuser:
	docker-compose exec $(WEB) python manage.py createsuperuser

shell:
	docker-compose exec $(WEB) python manage.py shell


# Start connections
up:
	docker-compose up

up-d:
	docker-compose up -d


# Stop containers
down:
	docker-compose down


# Build containers
build:
	docker-compose -f docker-compose.yml build

rebuild:
	docker-compose build --no-cache


# Run tests
test:
	docker-compose exec $(WEB) python manage.py test


# Linting
lint:
	flake8 .
	isort --check-only .
	black --check .


# Format code
format:
	black .
	flake8 .
	isort .