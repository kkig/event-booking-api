# -----------------------------------------------------------------------------
# Docker Commands
# -----------------------------------------------------------------------------

# Docker service name (as defined in compose.yml)
WEB=web

# Tells Make to always run the specified targes,
# even if folders/files with the same name exist in the root directory.
.PHONY: \
	up up-detach down build rebuild \
	prod-up prod-down prod-build prod-rebuild prod-migrate \
	db db-detach db-down

DEV_PROJECT := event-booking-dev
PROD_PROJECT := event-booking-prod

DEV_COMPOSE := docker compose -p $(DEV_PROJECT) -f compose.yml -f compose.dev.yml
PROD_COMPOSE := docker compose -p $(PROD_PROJECT) -f compose.yml -f compose.prod.yml


# Build all dev containers
build:
	$(DEV_COMPOSE) build

# Rebuild dev containers from scratch (no cache)
rebuild:
	$(DEV_COMPOSE) build --no-cache

# Start all dev services (foreground)
up:
	$(DEV_COMPOSE) up --build

# Start all dev services (detached mode)
up-detach:
	$(DEV_COMPOSE) up --build -d

# Stop all dev services and remove containers
down:
	$(DEV_COMPOSE) down


# Build prod web container
prod-build:
	$(PROD_COMPOSE) build web

# Rebuild prod web container from scratch (no cache)
prod-rebuild:
	$(PROD_COMPOSE) build --no-cache web

# Run prod migrations
prod-migrate:
	$(PROD_COMPOSE) run --rm web python manage.py migrate

# Start all prod services (detached mode)
prod-up:
	$(PROD_COMPOSE) up -d

# Start all prod services and remove containers
prod-down:
	$(PROD_COMPOSE) down


# Run db container only (foreground)
db:
	$(DEV_COMPOSE) up db

# Run db container only (detached mode)
db-detach:
	$(DEV_COMPOSE) up -d db

# Stop db container only
db-down:
	$(DEV_COMPOSE) stop db
