from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from django.db import transaction
from core.models import Query, QueryCategory
from core.services import validate_select_only
from mahou.models import Snapshot


class Command(BaseCommand):
    help = "Instala consultas y categoría privada Mahou; no ejecuta SQL externo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--update-sql",
            action="store_true",
            help="Reemplaza SQL de las dos consultas existentes por la versión incluida.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        group, _ = Group.objects.get_or_create(name="Mahou")
        category, created = QueryCategory.objects.get_or_create(
            name="Mahou", defaults={"order": 50}
        )
        if created:
            category.allowed_groups.add(group)
        elif not category.allowed_groups.exists():
            raise CommandError(
                "La categoría Mahou existente es pública. Restringe sus grupos antes de instalar."
            )
        for suffix, name, source in [
            ("PANEL", "Panel Mahou Steel", "panel"),
            ("MUELLES", "Ocupación de muelles Mahou", "muelles"),
        ]:
            sql = (Path(__file__).resolve().parents[2] / (source + ".sql")).read_text(
                encoding="utf-8"
            )
            validate_select_only(sql)
            q, made = Query.objects.get_or_create(
                code="MAHOU_" + suffix,
                defaults={
                    "name": name,
                    "category": category,
                    "sql": sql,
                    "database_alias": "mahou",
                    "description": "Importada de PANEL MAHOU Steel v17.1. Solo datos XGA. Dashboard: /mahou/.",
                },
            )
            if not made and options["update_sql"]:
                q.sql = sql
                q.database_alias = "mahou"
                q.save(update_fields=["sql", "database_alias"])
            self.stdout.write(q.code + (" creada" if made else " existente"))
        Snapshot.objects.get_or_create(pk=1)
        self.stdout.write(
            "Añade los usuarios autorizados al grupo Mahou. Configura MAHOU_DSN y reinicia worker/scheduler/web."
        )
