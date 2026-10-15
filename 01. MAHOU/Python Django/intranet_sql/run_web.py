import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "intranet_sql.settings")
from intranet_sql.wsgi import application
from django.conf import settings
from waitress import serve

if __name__ == "__main__":
    options = {}
    if os.getenv("TRUST_PROXY_HEADERS", "").lower() in ("true", "1", "yes"):
        options = {
            "trusted_proxy": "127.0.0.1",
            "trusted_proxy_headers": {"x-forwarded-proto"},
            "trusted_proxy_count": 1,
        }
    serve(application, listen="127.0.0.1:8000", threads=4, **options)
