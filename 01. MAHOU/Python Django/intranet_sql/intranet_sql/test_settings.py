import os

os.environ["DJANGO_SECRET_KEY"] = "test-only-not-for-deployment-key-2026"
os.environ["EXTERNAL_DB_ENABLED"] = "false"
from .settings import *

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
SECURE_SSL_REDIRECT = False
MAIL_PROVIDER = "file"
