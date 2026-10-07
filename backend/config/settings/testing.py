from .base import *

DEBUG = False

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Required for sending emails
DEFAULT_FROM_EMAIL = "no-reply@mydomain.com"

# Error emails will come here
SERVER_EMAIL = DEFAULT_FROM_EMAIL

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        }
    },
}
