# -----------------------------------------------------------------------------
# Docker Commands
# -----------------------------------------------------------------------------

# Docker service name (as defined in docker-compose.yml)
WEB=web

# Tells Make to always run the specified targes,
# even if folders/files with the same name exist in the root directory.
.PHONY: up up-detach down build rebuild


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
