WEB=web

# Run management commands
migrate:
	docker-compose exec $(WEB) python manage.py migrate

makemigrations:
	docker-compose exec $(WEB) python manage.py makemigrations