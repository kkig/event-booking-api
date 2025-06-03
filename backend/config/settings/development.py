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

# === Email configuration for Development ===

# Prints emails to console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Required for sending emails
DEFAULT_FROM_EMAIL = "no-reply@mydomain.com"

# Error emails will come here
SERVER_EMAIL = DEFAULT_FROM_EMAIL
