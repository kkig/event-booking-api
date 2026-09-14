from decouple import Csv

from .base import *

# DEBUG must be False in production
DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())
