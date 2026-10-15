import csv
import io
from datetime import timedelta
from unittest.mock import patch
from django.test import TestCase, Client, override_settings
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from core.models import Query
from core.services import QueryValidationError, validate_select_only
from reports.scheduling import fingerprint
from .models import Snapshot
from .services import (
    queries_for,
    signatures,
    request_refresh,
    process_refresh,
    auto_refresh,
    collect,
)
from .data import FIELDS, filtered, present, summary, dock_groups, occupancy


def row(**extra):
    r = {key: None for key, _, _ in FIELDS}
    r.update(
        {
            "1_EstadoFechaTeoricaCarga": "Hoy",
            "6_EstadoAbiertoCerrado": "Abierto",
            "2_Albaran": "000123",
            "7_TipoEstadoConvertido": "20",
            "5_FechaTeoricaCargaDoc": "2026-10-05T08:30:00",
            "21_PorcTotalPalets": "100.0",
            "23_PorcPickingCajas": 50,
            "31_UbicacionesPendientesCarga": "CA-00-001-00 | CA-00-002-00",
        }
    )
    r.update(extra)
    return r


class DashboardTests(TestCase):
    def setUp(self):
        call_command("install_mahou", stdout=io.StringIO())
        self.user = get_user_model().objects.create_user("mahou", password="test")
        self.user.groups.add(Group.objects.get(name="Mahou"))
        self.client.force_login(self.user)
        self.queries = queries_for(self.user)
        Snapshot.objects.filter(pk=1).update(
            status="done",
            updated_at=timezone.now(),
            signatures=signatures(self.queries),
            rows=[row()],
            docks=[
                {
                    "UbicacionCompleta": "DE-00-001-00",
                    "NumPalets": 0,
                    "FechaEntradaMin": None,
                }
            ],
        )

    def test_install_private_idempotent_and_sql(self):
        call_command("install_mahou", stdout=io.StringIO())
        self.assertEqual(Query.objects.filter(code__startswith="MAHOU_").count(), 2)
        for q in self.queries:
            validate_select_only(q.sql)
            self.assertEqual(q.database_alias, "mahou")
        self.assertTrue(self.queries[0].category.allowed_groups.exists())

    def test_access_and_revocation_all_endpoints(self):
        self.user.groups.clear()
        for url in ["/mahou/", "/mahou/?format=csv"]:
            self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.post("/mahou/actualizar/").status_code, 403)
        self.client.logout()
        self.assertEqual(self.client.get("/mahou/").status_code, 302)

    def test_disabled_second_query_denies_shared_snapshot(self):
        self.queries[1].is_active = False
        self.queries[1].save()
        self.assertEqual(self.client.get("/mahou/").status_code, 403)

    def test_page_filter_csv_no_sql(self):
        with patch("mahou.services.stream_query") as sql:
            r = self.client.get("/mahou/")
            self.assertContains(r, "000123")
            self.assertContains(r, "100 %")
            self.assertContains(r, "Panel Mahou Steel")
            csv_response = self.client.get(
                "/mahou/?period=Hoy&status=Abierto&format=csv"
            )
            records = list(
                csv.reader(
                    io.StringIO(csv_response.content.decode("utf-8-sig")), delimiter=";"
                )
            )
            self.assertEqual(len(records), 2)
            self.assertEqual(len(records[0]), 18)
            self.assertEqual(records[1][0], "000123")
            sql.assert_not_called()

    def test_invalid_filter_and_empty_results(self):
        self.assertEqual(self.client.get("/mahou/?period=INVALID").status_code, 400)
        r = self.client.get("/mahou/?period=Futuro")
        self.assertContains(r, "No hay pedidos")

    def test_csv_injection_and_html_escape(self):
        Snapshot.objects.filter(pk=1).update(
            rows=[
                row(
                    **{
                        "13_NombreDireccion": '=HYPERLINK("bad")',
                        "14_Comentario": "<script>alert(1)</script>",
                    }
                )
            ]
        )
        self.assertContains(self.client.get("/mahou/"), "&lt;script&gt;")
        self.assertIn(
            "'=HYPERLINK", self.client.get("/mahou/?format=csv").content.decode()
        )

    def test_changed_query_hides_old_snapshot(self):
        self.queries[0].sql += "\n-- changed"
        self.queries[0].save()
        self.assertNotContains(self.client.get("/mahou/"), "000123")
        self.assertEqual(self.client.get("/mahou/?format=csv").status_code, 409)

    def test_refresh_post_csrf_and_coalescing(self):
        self.assertEqual(self.client.get("/mahou/actualizar/").status_code, 405)
        csrf = Client(enforce_csrf_checks=True)
        csrf.force_login(self.user)
        self.assertEqual(csrf.post("/mahou/actualizar/").status_code, 403)
        self.assertTrue(request_refresh(self.user))
        self.assertFalse(request_refresh(self.user))

    def test_complete_pair_published_and_failure_preserves_it(self):
        request_refresh(self.user)
        with patch(
            "mahou.services.collect", side_effect=[[row(**{"2_Albaran": "NEW"})], []]
        ):
            self.assertTrue(process_refresh())
        s = Snapshot.objects.get(pk=1)
        self.assertEqual(s.rows[0]["2_Albaran"], "NEW")
        self.assertEqual(s.status, "done")
        Snapshot.objects.filter(pk=1).update(
            requested_at=timezone.now() - timedelta(minutes=5)
        )
        request_refresh(self.user)
        with patch(
            "mahou.services.collect",
            side_effect=[[row()], RuntimeError("test failure")],
        ):
            process_refresh()
        s.refresh_from_db()
        self.assertEqual(s.status, "failed")
        self.assertEqual(s.rows[0]["2_Albaran"], "NEW")

    def test_permission_revoked_during_refresh_not_published(self):
        request_refresh(self.user)

        def revoke(*args):
            self.user.groups.clear()
            return []

        with patch("mahou.services.collect", side_effect=revoke):
            process_refresh()
        self.assertEqual(Snapshot.objects.get(pk=1).status, "failed")

    @override_settings(MAHOU_MAX_ROWS=1)
    def test_cap_and_schema_reject_partial_data(self):
        def fake(q, u, p, consume):
            consume(["key"], None)
            consume(["key"], [[1], [2]])

        with patch("mahou.services.stream_query", side_effect=fake):
            with self.assertRaises(ValueError):
                collect(self.queries[0], self.user, ["key"])
            with self.assertRaises(ValueError):
                collect(self.queries[0], self.user, ["missing"])

    @override_settings(MAHOU_AUTO_REFRESH_USER="mahou", MAHOU_REFRESH_SECONDS=900)
    def test_scheduler_cooldown(self):
        auto_refresh()
        self.assertEqual(Snapshot.objects.get(pk=1).status, "pending")
        Snapshot.objects.filter(pk=1).update(status="failed")
        auto_refresh()
        self.assertEqual(Snapshot.objects.get(pk=1).status, "failed")

    def test_states_filters_multiple_docks_and_no_invented_totals(self):
        rows = [
            row(),
            row(**{"2_Albaran": "000124", "7_TipoEstadoConvertido": "20-INC"}),
        ]
        self.assertEqual(len(filtered(rows, {"albaran": "124"})), 1)
        self.assertEqual(summary(rows)[0][2][1], "1")
        self.assertEqual([g["count"] for g in dock_groups(rows)], [2, 2])
        self.assertEqual(present(rows)[0][7]["value"], "100 %")
        self.assertEqual(occupancy([{"NumPalets": None}])[0]["status"], "Sin dato")

    def test_stale_snapshot_notice(self):
        Snapshot.objects.filter(pk=1).update(
            updated_at=timezone.now() - timedelta(days=1)
        )
        self.assertContains(self.client.get("/mahou/"), "pueden estar desactualizados")


class ConnectionRoutingTests(TestCase):
    @override_settings(
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
            "mahou": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
        }
    )
    def test_stream_uses_configured_alias_not_default(self):
        from unittest.mock import MagicMock
        from core.services import stream_query

        user = get_user_model().objects.create_superuser("root", password="test")
        q = Query.objects.create(
            code="ROUTE", name="route", sql="SELECT 1", database_alias="mahou"
        )
        cursor = MagicMock()
        cursor.description = [("result",)]
        cursor.fetchmany.side_effect = [[(1,)], []]
        connection = MagicMock()
        connection.cursor.return_value.__enter__.return_value = cursor
        connections = MagicMock()
        connections.__getitem__.return_value = connection
        with patch("core.services.connections", connections):
            stream_query(q, user, {}, lambda *a: None)
        connections.__getitem__.assert_called_once_with("mahou")

    def test_worker_processes_both_queues(self):
        from reports.engine import process_work

        with patch(
            "mahou.services.process_refresh", return_value=True
        ) as refresh, patch(
            "reports.engine.process_job", return_value=False
        ) as reports:
            self.assertTrue(process_work())
            refresh.assert_called_once()
            reports.assert_called_once()
