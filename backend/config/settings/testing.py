from .base import *

DEBUG = False

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Required for sending emails
DEFAULT_FROM_EMAIL = "no-reply@mydomain.com"

# Error emails will come here
SERVER_EMAIL = DEFAULT_FROM_EMAIL
