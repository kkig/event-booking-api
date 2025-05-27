from .base import *

# DEBUG must be False in production
DEBUG = config("DEBUG", default=False, cast=bool)

# ALLOWED_HOSTS must be explicitly set to your production domain(s)
# It's best to read these from an OS environment variable in production
# config() will pick it up from the OS environment, if set.
# Example: ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost")

INSTALLED_APPS += []

MIDDLEWARE += []

DATABASES["default"].update(
    {
        "HOST": config("POSTGRES_HOST", default="db"),
        "PORT": config("POSTGRES_PORT", default="5432"),
    }
)
