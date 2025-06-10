# Event Ticketing / Booking API

![Python](https://img.shields.io/badge/python-3.13-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Lint Checks](https://github.com/kkig/event-booking-api/actions/workflows/lint.yml/badge.svg)

A backend REST API built with Django REST Framework and JWT authentication to manage events, ticket types, and bookings with concurrency-safe logic.
Designed for multi-ticket bookings, capacity management, and robust concurrency control using database transactions and row-level locking.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [User Roles](#user-roles)
- [API Endpoints Overview](#api-endpoints-overview)
- [API Documentation](#api-documentation)
- [Concurrency Handling](#concurrency-handling)
- [Running Tests](#running-tests)
- [Makefile Commands](#makefile-commands)
- [Pre-commit Hooks](#pre-commit-hooks)
- [CI / GitHub Actions](#ci--github-actions)
- [Future Improvements](#future-improvements)

## Features

- 🚀 Handles concurrent booking requests gracefully, preventing race conditions
- User registration and authentication with role-based permissions
- Create and manage events with capacity limits
- Define multiple ticket types per event (e.g., Standard, VIP)
- Booking creation with atomic transactions and pessimistic locking (`select_for_update()`) to prevent overbooking
- Booking cancellation that releases ticket availability
- Comprehensive automated tests simulating real-world concurrency scenarios

## Tech Stack

- Python 3.13, Django 5.2.1
- Django REST Framework
- PostgreSQL (leveraging row-level locking and transactions)
- Redis (used for Celery and caching if added later)
- Pytest for testing, including concurrency tests with threading
- drf-spectacular for auto-generated OpenAPI docs
- Optional:
  - Docker and Docker Compose (for containerized setup)

## Setup & Installation

### Prerequisites

- Python 3.13
- PostgreSQL (with a database and user ready)
- (Optional) Docker and Docker Compose for containerized setup

### Installation Steps

1. Clone the repo:
   ```bash
   git clone https://github.com/kkig/event-booking-api.git
   cd event-booking-api
   ```
2. Create a `.env` file based on `.env.example` and update environment variables as needed.
3. Build and start containers (this will build the Docker images and start services such as Django app, PostgreSQL, Redis):
   ```bash
   docker-compose up -d --build
   ```
4. Run database migrations inside the Django container:
   ```bash
   docker-compose exec web python manage.py migrate
   ```
5. (Optional) Create a superuser inside the Django container:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```
6. The API server will be accessible at `http://localhost:8000` by default.
7. To stop the containers:
   ```bash
   docker-compose down
   ```

## User Roles

- **Organizer** – Can create and manage events and ticket types.
- **Attendee** – Can browse events and make/cancel bookings.

## API Endpoints Overview

### Accounts

| Endpoint                                             | Method | Description                              | Auth Required |
| ---------------------------------------------------- | ------ | ---------------------------------------- | ------------- |
| `/api/auth/register/`                                | POST   | Create new account                       | No            |
| `/api/auth/login/`                                   | POST   | Log in user                              | No            |
| `/api/auth/token/refresh/`                           | POST   | Exchange access token with refresh token | No            |
| `/api/auth/profile/`                                 | GET    | Retrieve details of the user             | Yes           |
| `/api/auth/profile/`                                 | PUT    | Update details of the user               | Yes           |
| `/api/auth/change-password/`                         | POST   | Reset password                           | Yes           |
| `/api/auth/password-reset-request/`                  | POST   | Initiate password reset flow             | No            |
| `/api/auth/password-reset-confirm/{uidb64}/{token}/` | POST   | Reset password                           | No            |
| `/api/auth/deactivate-account/`                      | DELETE | Deactivate user account                  | Yes           |

### Bookings

| Endpoint                     | Method | Description                 | Auth Required  |
| ---------------------------- | ------ | --------------------------- | -------------- |
| `/api/bookings/`             | POST   | Create a new booking        | Yes (Attendee) |
| `/api/bookings/{id}/`        | GET    | Retrieve details of booking | Yes (Owner)    |
| `/api/bookings/{id}/cancel/` | PUT    | Cancel an existing booking  | Yes (Owner)    |
| `/api/users/me/bookings/`    | GET    | List all bookings           | Yes (Owner)    |

### Events

| Endpoint                        | Method | Description                    | Auth Required   |
| ------------------------------- | ------ | ------------------------------ | --------------- |
| `/api/events/`                  | GET    | List active/upcoming events    | No              |
| `/api/events/`                  | POST   | List active/upcoming events    | Yes (Organizer) |
| `/api/events/{id}/`             | GET    | Retrieve event details         | No              |
| `/api/events/{id}/`             | PUT    | Update event details           | Yes (Owner)     |
| `/api/events/{id}/`             | DELETE | Delete event                   | Yes (Owner)     |
| `/api/events/{id}/ticket-types` | GET    | List ticket types for an event | Yes (Owner)     |
| `/api/events/{id}/ticket-types` | POST   | Create a ticket type for event | Yes (Owner)     |

_Note: Authentication uses token-based auth (JWT) for securing endpoints._

## API Documentation

Interactive API docs are available once the server is running:

| Type           | URL                 | Description                       |
| -------------- | ------------------- | --------------------------------- |
| OpenAPI Schema | `/api/schema`       | Raw OpenAPI schema (JSON)         |
| Swagger UI     | `/api/docs/swagger` | Interactive Swagger documentation |
| ReDoc UI       | `/api/docs/redoc`   | Interactive ReDoc documentation   |

These routes are powered by [drf-spectacular](https://drf-spectacular.readthedocs.io/), and automatically generated based on your serializers, views, and schema annotations.

> 🔐 To authorize in Swagger UI, click the "Authorize" button and enter your JWT token as:
> `Bearer <your-token>`

## Concurrency Handling

To prevent overbooking under concurrent booking attempts:

- All booking creations run inside `transaction.atomic()` blocks.
- Ticket types and events are locked with `select_for_update()` to ensure row-level locking.
- Ticket availability and event capacity are checked and updated atomically.
- Automated tests simulate concurrent booking attempts with multiple threads, ensuring that only one booking succeeds when capacity is limited.

### Booking Flow

[Mermaid sequence diagram](https://mermaid.live) that visualizes booking creation flow with concurrency control.

<details>
sequenceDiagram
    participant A as Attendee
    participant C as API Server
    participant D as Database

    A->>C: POST /api/bookings/
    C->>C: Begin transaction.atomic()
    C->>D: SELECT TicketType FOR UPDATE
    C->>D: SELECT Event FOR UPDATE
    C->>D: Check availability & capacity

    alt Tickets Available
        C->>D: Create Booking
        C->>D: Set Booking status to CONFIRMED
        C->>D: Decrement TicketType.quantity_available
        C->>D: Increment TicketType.quantity_sold
        C->>D: Commit Transaction
        C-->>A: 201 Created (Booking Confirmed)
    else Sold Out
        C->>D: Rollback Transaction
        C-->>A: 400 Bad Request (Sold Out)
    end

</details>

### Booking Cancellation Flow

[Mermaid sequence diagram](https://mermaid.live) that visualizes booking cancellation flow with concurrency control.

<details>
sequenceDiagram
    participant A as Attendee
    participant C as API Server
    participant D as Database

    A->>C: PUT /api/bookings/:id/
    C->>C: Check auth and ownership
    C->>D: Begin transaction.atomic()
    C->>D: Lock Booking (SELECT ... FOR UPDATE)
    C->>D: Check Booking status
    alt Already cancelled
        C-->>A: 400 Bad Request (already cancelled)
    else Valid cancellation
        C->>D: Update Booking status to CANCELLED
        C->>D: Increment TicketType.quantity_available
        C->>D: Decrement TicketType.quantity_sold
        C->>D: Commit transaction
        C-->>A: 200 OK (cancelled)
    end

</details>

## Running Tests

Run tests inside the Docker container:

```bash
docker-compose exec web pytest --maxfail=1 --disable-warnings -q
```

### Concurrency Test Suite

A key aspect of this API is its robust handling of concurrent booking requests. The test suite includes specific tests designed to validate the system's behavior under high-stress, simultaneous interactions.

These tests utilize Python's `threading` module within Pytest to simulate multiple users attempting to book tickets concurrently. They ensure that:

- **No Overbooking:** Even with multiple simultaneous requests, the system prevents tickets from being oversold beyond available capacity
- **Race Condition Prevention:** Scenarios like two users attempting to book the very last available ticket are handled correctly, with only one request succeeding.
- **Shared Capacity Management:** Tests cover situations where different ticket types contribute to a single event's overall capacity, ensuring accurate availability updates across types.
- **Atomic Operations:** Verifies that critical operations (booking creation, quantity updates, cancellations) are atomic and concurrency-safe, leveraging PostgreSQL's row-level locking (`select_for_update()`) and Django's `transaction.atomic()` blocks.
- **Cancellation Releasing Tickets:** Confirms that cancelling a booking correctly frees up ticket availability for other users to book immediately.

These dedicated concurrency tests provide strong confidence in the API's reliability under real-world usage patterns.

## Makefile Commands

This project includes a `Makefile` to simplify common development tasks:

### Development

| Command        | Description                          |
| -------------- | ------------------------------------ |
| `make up`      | Start all services in the foreground |
| `make up-d`    | Start all services in detached mode  |
| `make down`    | Stop and remove containers           |
| `make build`   | Build containers                     |
| `make rebuild` | Rebuild containers without cache     |

### Django Management

| Command                | Description                            |
| ---------------------- | -------------------------------------- |
| `make migrate`         | Apply database migrations              |
| `make migrations`      | Create new migration files             |
| `make createsuperuser` | Create Django superuser                |
| `make shell`           | Open Django shell inside the container |

### Testing & Linting

| Command       | Description                                     |
| ------------- | ----------------------------------------------- |
| `make test`   | Run tests with pytest                           |
| `make lint`   | Run Flake8, isort, and Black in check-only mode |
| `make format` | Auto-format code with Black, Flake8, isort      |

These commands work inside the Docker environment, and make day-to-day development faster and easier.

## Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to ensure code quality by running linters and formatters automatically before each commit.

### Setup

1. Install pre-commit:
   ```bash
   pip install pre-commit
   ```
2. Install the hooks:
   ```bash
   pre-commit install
   ```
3. (Optional) Run all hooks manually:
   ```bash
   pre-commit run --all-files
   ```

### Configured Hooks

These hooks are defined in `.pre-commit-config.yaml`:

- ✅ [black](https://github.com/psf/black) – Python code formatter
- ✅ [isort](https://github.com/PyCQA/isort) – Sorts and organizes Python imports
- ✅ [flake8](https://github.com/PyCQA/flake8) – Python linter
- ✅ [codespell](https://github.com/codespell-project/codespell) – Spell checker for `.md` files

## CI / GitHub Actions

This project uses GitHub Actions to automatically check code formatting and linting on each push or pull request to `master` and `dev` branches.

### Workflow: `Lint & Format Checks`

Located in `.github/workflows/lint.yml`, this workflow ensures:

- ✅ [black](https://github.com/psf/black) – Code is correctly formatted
- ✅ [isort](https://github.com/PyCQA/isort) – Imports are sorted
- ✅ [flake8](https://github.com/PyCQA/flake8) – Code follows linting rules

The workflow runs on every push and PR to `master` or `dev`, helping catch issues early in CI.

## Future Improvements

- Implement email notifications for booking confirmation and cancellation
- Add rate limiting to prevent abuse
- Enhance error response standardization
- Expand user role management (organizer vs attendee)

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
