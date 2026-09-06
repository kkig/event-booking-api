# Event Ticketing / Booking API

![Python](https://img.shields.io/badge/python-3.14-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Lint Checks](https://github.com/kkig/event-booking-api/actions/workflows/ci.yml/badge.svg)

A backend REST API built with Django REST Framework and JWT authentication to manage events, ticket types, and bookings.

The API is designed to maintain ticket inventory and event-capacity consistency under concurrent booking and cancellation requests, using PostgreSQL transactions and row-level locking.


## Features

- User registration and JWT authentication with role-based permissions
- Create and manage events with capacity limits
- Define multiple ticket types per event
- Create, view, and cancel bookings
- Concurrency-safe booking creation using database transactions and row-level locking
- Event-level capacity enforcement across multiple ticket types
- Atomic booking cancellation that restores ticket inventory
- Automated concurrency tests covering competing bookings, shared event capacity, and booking/cancellation races


## Tech Stack

- Python 3.14
- Django & Django REST Framework
- PostgreSQL
- JWT authentication
- Docker & Docker Compose
- pytest / pytest-django
- Ruff
- GitHub Actions


## Project Structure

```text
.
├── backend/           # Django application and Python dependencies
├── docs/              # Project documentation
├── scripts/           # Development/setup scripts
├── .devcontainer/     # Dev Container configuration
├── compose.yml        # Base Docker Compose configuration
├── compose.dev.yml    # Development environment
├── compose.prod.yml   # Production environment
├── Makefile           # Common development commands
├── .env.example
├── LICENSE
├── README.md
└── project.code-workspace
```


## Getting Started

1. Clone the repository:
    ```bash
    git clone https://github.com/kkig/event-booking-api.git
    cd event-booking-api
    ```
2. Create your environment file:
    ```bash
    cp .env.example .env
    ```

Choose one of the following development workflows:

- **Development Container** - quickest way to get started with the preconfigured development environment.
- **Local Development** - install and manage the development environment on your own machine.

For detailed setup instructions, see [Development Guide](docs/development.md).


## Running the Application

### Development Container

The development environment is configured automatically when using the Development Container.

The API is available at:
`http://localhost:8000`


### Local Development

Start the development environment:
```bash
make up
```

To stop the application:
```bash
make down
```

## Documentation

- [Development Guide](docs/development.md)
- [Architecture](docs/architecture.md)


## User Roles

- **Organizer** – Can create and manage events and ticket types.
- **Attendee** – Can browse events and create/cancel bookings.


## API Documentation

Interactive API documentation is available once the server is running:

| Type           | Endpoint            | Description                       |
| -------------- | ------------------- | --------------------------------- |
| OpenAPI Schema | `/api/schema`       | Raw OpenAPI schema (JSON)         |
| Swagger UI     | `/api/docs/swagger` | Interactive Swagger documentation |
| ReDoc UI       | `/api/docs/redoc`   | Interactive ReDoc documentation   |

> 🔐 To authenticate in Swagger UI, click **Authorize** and enter your JWT token:
> `Bearer <your-token>`


## Future Improvements

- Add asynchronous email notifications for booking confirmation and cancellation
- Add API rate limiting and caching for high-traffic endpoints
- Expand the API with payment processing and a full booking/payment lifecycle


## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
