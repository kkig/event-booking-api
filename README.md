# Multi-Currency Expense Tracker API

An API backend for tracking expenses across multiple currencies. Built with Django, PostgreSQL, and Docker. This project demonstrates clean code, modular structure, authentication, testing, and CI/CD workflows.

---

## Features

- Multi-currency expense tracking
- JWT Authentication (WIP)
- Dockerized environment
- PostgreSQL database
- Modular Django architecture
- GitHub Actions CI pipeline
- Pre-commit hooks with Black, Flake8, and isort

---

## Tech Stack

- Python 3.13
- Django 5.2.1
- PostgreSQL 14
- Docker & Docker Compose
- Celery + Redis (planned)
- GitHub Actions for CI/CD

---

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- Make (optional but recommended)

### Clone the repo

```bash
git clone https://github.com/kkig/expense-tracker-api.git
cd expense-tracker-api
```

## Run the app

```bash
make build              # Build containers
make up                 # Start services
make migrate            # Apply migrations
make createsuperuser    # Create admin user
```

## Format code

```bash
make format
```

## Project Structure

```
expense-tracker-api/
│
├── config/                  # Django settings package
├── tracker/                 # Main app (models, views, etc.)
├── .github/                 # GitHub Actions workflows & PR templates
├── .env.example             # Example environment config
├── docker-compose.yml       # Docker services
├── Dockerfile               # Web services Docker image
├── Makefile                 # Shortcuts for common commands
└── README.md                # Project docs
```

## Development Workflow

- Branch from `dev`
- Use `feature/<your-feature>` naming
- Push and open PR to `dev`
- Auto-reviewers and labels will be assigned automatically
- PR template will be applied
- After approval, merge to `dev`, then eventually to `main`

## Authentication

WIP

## Testing

WIP

## License

MIT License
