from .base import *

DEBUG = True

# Overrides ALLOWED_HOSTS (from .env) for development
ALLOWED_HOSTS = ["*"]

# Development-specific sinstalled apps(e.g. for Django Debug Toolbar)
INSTALLED_APPS += []

TEMPLATES += []

# Development-specific middleware (if using debug toolbar)
MIDDLEWARE += []

# === Email configuration for Development ===

# Prints emails to console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Required for sending emails
DEFAULT_FROM_EMAIL = "no-reply@mydomain.com"

# Error emails will come here
SERVER_EMAIL = DEFAULT_FROM_EMAIL
