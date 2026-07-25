# Event Ticketing / Booking API

![Python](https://img.shields.io/badge/python-3.14-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Lint Checks](https://github.com/kkig/event-booking-api/actions/workflows/ci.yml/badge.svg)

A backend REST API built with Django REST Framework and JWT authentication to manage events, ticket types, and bookings with concurrency-safe logic.
Designed for multi-ticket bookings, capacity management, and robust concurrency control using database transactions and row-level locking.


## Features

- 🚀 Handles concurrent booking requests gracefully, preventing race conditions
- User registration and authentication with role-based permissions
- Create and manage events with capacity limits
- Define multiple ticket types per event (e.g., Standard, VIP)
- Booking creation with atomic transactions and pessimistic locking (`select_for_update()`) to prevent overbooking
- Booking cancellation that releases ticket availability
- Comprehensive automated tests simulating real-world concurrency scenarios


## Tech Stack

- Python 3.14
- Django REST Framework
- uv
- PostgreSQL
- Docker & Docker Compose


## Project Structure
This repository is organized as a monorepo.

```text
.
├── backend/           # Django application
├── docs/              # Project documentation
├── .devcontainer/     # Dev Container configuration
├── .scripts           # Scripts
├── compose.yml        # Base development stack
├── compose.dev.yml    # Local development stack
├── compose.dev.yml    # Production development stack
├── Makefile           # Infrastructure commands
└── README.md
```

The Django project and all Python tooling (`pyproject.toml`, `uv.lock`, virtual environment, etc.) live inside the `backend/` directory.


## Getting Started

1. Clone the repository.
   ```bash
   git clone https://github.com/kkig/event-booking-api.git
   cd event-booking-api
   ```
2. Create a `.env` file from `.env.example`.

Choose one of the following development workflows:

- **Development Container** - quickest way to get started. Automatically configure development environment with required tools.
- **Local Development** - install and manage the development environment on your own machine.

For detailed setup instructions, see [Development Guide](docs/development.md).


## Running the Application

Start the development environment:
```bash
make up
```
To stop app:
```bash
make down
```

The API is available at:
`http://localhost:8000`


## Documentation

- [Development Guide](docs/development.md)
- [Architecture](docs/architecture.md)


## User Roles

- **Organizer** – Can create and manage events and ticket types.
- **Attendee** – Can browse events and make/cancel bookings.


## API Documentation

Interactive API docs are available once the server is running:

| Type           | URL                 | Description                       |
| -------------- | ------------------- | --------------------------------- |
| OpenAPI Schema | `/api/schema`       | Raw OpenAPI schema (JSON)         |
| Swagger UI     | `/api/docs/swagger` | Interactive Swagger documentation |
| ReDoc UI       | `/api/docs/redoc`   | Interactive ReDoc documentation   |

> 🔐 To authorize in Swagger UI, click the "Authorize" button and enter your JWT token as:
> `Bearer <your-token>`


## Future Improvements

- Implement email notifications for booking confirmation and cancellation
- Add rate limiting to prevent abuse
- Enhance error response standardization
- Expand user role management (organizer vs attendee)


## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
