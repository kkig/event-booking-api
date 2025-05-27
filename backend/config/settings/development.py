from .base import *

# Overrides DEBUG (from .env) for development
DEBUG = config("DEBUG", default=True, cast=bool)

# Overrides ALLOWED_HOSTS (from .env) for development
ALLOWED_HOSTS = ["*"]

# Development-specific sinstalled apps(e.g. for Django Debug Toolbar)
INSTALLED_APPS += []

TEMPLATES += []

# Development-specific middleware (if using debug toolbar)
MIDDLEWARE += []

# Optionally override database settings
DATABASES["default"].update(
    {
        "HOST": config("POSTGRES_HOST", default="db"),  # Docker service name
        "PORT": config("POSTGRES_PORT", default="5432"),
    }
)
