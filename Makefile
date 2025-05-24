WEB=web

# Run management commands
migrate:
	docker-compose exec $(WEB) python manage.py migrate

makemigrations:
	docker-compose exec $(WEB) python manage.py makemigrations


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
