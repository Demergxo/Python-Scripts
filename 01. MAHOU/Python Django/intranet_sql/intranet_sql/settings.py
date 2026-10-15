from pathlib import Path
import os
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=False)


def flag(key, default=False):
    return os.getenv(key, str(default)).lower() in ("1", "true", "yes")


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    raise ImproperlyConfigured(
        "Configura DJANGO_SECRET_KEY en .env (ver .env.example)."
    )
DEBUG = flag("DJANGO_DEBUG")
ALLOWED_HOSTS = [
    x.strip()
    for x in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if x.strip()
]
CSRF_TRUSTED_ORIGINS = [
    x.strip()
    for x in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if x.strip()
]
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core.apps.CoreConfig",
    "reports",
    "mahou",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "intranet_sql.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "mahou.context.navigation",
            ]
        },
    }
]
WSGI_APPLICATION = "intranet_sql.wsgi.application"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.getenv("APP_DB_PATH", str(BASE_DIR / "db.sqlite3")),
        "OPTIONS": {"timeout": 30, "transaction_mode": "IMMEDIATE"},
    }
}
EXTERNAL_DB_ENABLED = flag("EXTERNAL_DB_ENABLED")
if EXTERNAL_DB_ENABLED:
    DATABASES["externa"] = {
        "ENGINE": "mssql",
        "NAME": os.getenv("XGA_DATABASE", "XGA"),
        "OPTIONS": {
            "dsn": os.getenv("XGA_DSN", "XGA_PROD"),
            "driver": os.getenv("XGA_DRIVER", "ODBC Driver 18 for SQL Server"),
            "extra_params": os.getenv(
                "XGA_EXTRA_PARAMS",
                "Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=no;",
            ),
            "query_timeout": int(os.getenv("XGA_QUERY_TIMEOUT", "1800")),
            "connection_timeout": 15,
        },
    }
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "es-es"
TIME_ZONE = "Europe/Madrid"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"
# Backend de sesiones DB: revocación al cerrar sesión. La migración ya existe.
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_SECURE = flag("HTTPS_ENABLED")
CSRF_COOKIE_SECURE = flag("HTTPS_ENABLED")
SECURE_SSL_REDIRECT = flag("HTTPS_ENABLED")
# Activar solo cuando el proxy elimina y establece esta cabecera; Waitress escucha en loopback.
if flag("TRUST_PROXY_HEADERS"):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
REPORT_ROOT = Path(os.getenv("REPORT_ROOT", str(BASE_DIR / "var" / "reports")))
REPORT_MAX_ROWS = min(int(os.getenv("REPORT_MAX_ROWS", "1000000")), 1048575)
MAIL_PROVIDER = os.getenv("MAIL_PROVIDER", "file").lower()
MAIL_FILE_PATH = Path(os.getenv("MAIL_FILE_PATH", str(BASE_DIR / "var" / "mail")))
MAIL_FROM = os.getenv("MAIL_FROM", "intranet@example.invalid")
MAIL_MAX_ATTACHMENT_BYTES = int(os.getenv("MAIL_MAX_ATTACHMENT_BYTES", "2000000"))
MAIL_MAX_ATTEMPTS = 3
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "25"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_TLS = flag("SMTP_TLS")
SMTP_SSL = flag("SMTP_SSL")
GRAPH_TENANT_ID = os.getenv("GRAPH_TENANT_ID", "")
GRAPH_CLIENT_ID = os.getenv("GRAPH_CLIENT_ID", "")
GRAPH_CLIENT_SECRET = os.getenv("GRAPH_CLIENT_SECRET", "")
GRAPH_SENDER = os.getenv("GRAPH_SENDER", "")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

# Mahou has its own DSN; never silently fall back to the production connection.
if flag("MAHOU_DB_ENABLED"):
    DATABASES["mahou"] = {
        "ENGINE": "mssql", "NAME": os.getenv("MAHOU_DATABASE", "XGA"),
        "OPTIONS": {
            "dsn": os.getenv("MAHOU_DSN", "conexion replicada"),
            "driver": os.getenv("MAHOU_DRIVER", "ODBC Driver 18 for SQL Server"),
            "extra_params": os.getenv("MAHOU_EXTRA_PARAMS", "Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=no;ApplicationIntent=ReadOnly;"),
            "query_timeout": int(os.getenv("MAHOU_QUERY_TIMEOUT", "300")),
            "connection_timeout": 15,
        },
    }
MAHOU_AUTO_REFRESH_USER = os.getenv("MAHOU_AUTO_REFRESH_USER", "")
MAHOU_REFRESH_SECONDS = max(60, int(os.getenv("MAHOU_REFRESH_SECONDS", "900")))
MAHOU_MAX_ROWS = max(1, int(os.getenv("MAHOU_MAX_ROWS", "20000")))
