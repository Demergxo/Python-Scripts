from django.apps import AppConfig
from django.db import connections

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        try:
            with connections["default"].cursor() as c:
                c.execute("PRAGMA journal_mode=WAL;")
                c.execute("PRAGMA synchronous=NORMAL;")
        except Exception:
            pass
