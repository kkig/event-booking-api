# -----------------------------------------------------------------------------
# Docker Commands
# -----------------------------------------------------------------------------

# Docker service name (as defined in compose.yml)
WEB=web

# Tells Make to always run the specified targes,
# even if folders/files with the same name exist in the root directory.
.PHONY: up up-detach down build rebuild


# Start all services (foreground)
up:
	docker compose \
		-f compose.yml \
		-f compose.dev.yml \
	up --build

# Start all services (detached mode)
up-detach:
	docker compose \
		-f compose.yml \
		-f compose.dev.yml \
	up --build -d

# Stop all services and remove containers
down:
	docker compose \
		-f compose.yml \
		-f compose.dev.yml \
	down

# Build all containers
build:
	docker compose \
		-f compose.yml \
		-f compose.dev.yml \
	build

# Rebuild containers from scratch (no cache)
rebuild:
	docker compose \
		-f compose.yml \
		-f compose.dev.yml \
	build --no-cache
