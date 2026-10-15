import csv
import tempfile
from datetime import datetime, timedelta, timezone as dtz
from pathlib import Path
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils import timezone
from openpyxl import load_workbook
from core.models import Query, QueryCategory, QueryParam
from core.forms import build_query_run_form
from core.services import QueryValidationError, validate_select_only
from .models import Job, Schedule, Delivery
from .scheduling import resolve_parameters, next_fire, fingerprint
from .engine import (
    create_job,
    enqueue_schedule,
    dispatch_due,
    process_job,
    process_mail,
)
from .mailer import MailFailure, graph_send, smtp_send
from .artifacts import artifact


class WorkflowTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.override = override_settings(
            REPORT_ROOT=Path(self.temp.name) / "reports",
            MAIL_FILE_PATH=Path(self.temp.name) / "mail",
            MAIL_PROVIDER="file",
        )
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.user = User.objects.create_user("owner", password="test", is_staff=True)
        self.other = User.objects.create_user("other", password="test")
        self.cat = QueryCategory.objects.create(name="KPI")
        self.q = Query.objects.create(
            code="OUT01", name="Outbound", sql="SELECT %s, %s", category=self.cat
        )
        for n, order in [("Fecha_Inicio", 1), ("Fecha_Fin", 2)]:
            QueryParam.objects.create(
                query=self.q,
                name=n,
                label=n,
                param_type="date",
                required=True,
                order=order,
            )
        self.params = {"Fecha_Inicio": "2026-09-01", "Fecha_Fin": "2026-09-30"}
        self.s = Schedule.objects.create(
            name="Mensual",
            query=self.q,
            owner=self.user,
            recipients="a@example.com;b@example.com",
            period="previous_month",
            frequency="monthly",
            enabled=True,
        )

    def job(self):
        return create_job(self.q, self.user, self.params)

    @staticmethod
    def fake_stream(q, user, params, consume):
        consume(["numero", "texto"], None)
        consume(["numero", "texto"], [(i, "=1+1") for i in range(501)])

    def test_uppercase_date_validation(self):
        f = build_query_run_form(self.q)(
            {"Fecha_Inicio": "2026-10-02", "Fecha_Fin": "2026-10-01"}
        )
        self.assertFalse(f.is_valid())

    def test_relative_month_across_year(self):
        p = resolve_parameters(self.s, datetime(2027, 1, 1, 6, tzinfo=dtz.utc))
        self.assertEqual(p, {"Fecha_Inicio": "2026-12-01", "Fecha_Fin": "2026-12-31"})

    def test_previous_week(self):
        self.s.period = "previous_week"
        p = resolve_parameters(self.s, datetime(2026, 10, 7, 6, tzinfo=dtz.utc))
        self.assertEqual(p["Fecha_Inicio"], "2026-09-28")
        self.assertEqual(p["Fecha_Fin"], "2026-10-04")

    def test_invalid_address_and_template_rejected(self):
        self.s.recipients = "not-a-mail"
        with self.assertRaises(Exception):
            self.s.full_clean()
        self.s.recipients = "a@example.com"
        self.s.subject = "{query.__class__}"
        with self.assertRaises(Exception):
            self.s.full_clean()

    def test_day_last_and_day31(self):
        self.s.month_day = "last"
        result = next_fire(self.s, datetime(2027, 2, 1, tzinfo=dtz.utc))
        self.assertEqual(result.day, 28)
        self.s.month_day = "31"
        self.assertEqual(
            next_fire(self.s, datetime(2027, 2, 1, tzinfo=dtz.utc)).month, 3
        )

    def test_interval_and_once(self):
        self.s.frequency = "hours"
        self.s.every_hours = 2
        self.s.once_at = datetime(2026, 10, 1, tzinfo=dtz.utc)
        self.assertEqual(
            next_fire(self.s, self.s.once_at), self.s.once_at + timedelta(hours=2)
        )
        self.s.frequency = "once"
        self.assertIsNone(next_fire(self.s, self.s.once_at))

    def test_dst_schedule_uses_madrid(self):
        self.s.frequency = "daily"
        self.s.hour = 6
        before = next_fire(self.s, datetime(2026, 10, 24, 0, tzinfo=dtz.utc))
        after = next_fire(self.s, datetime(2026, 10, 25, 0, tzinfo=dtz.utc))
        self.assertEqual(before.hour, 6)
        self.assertEqual(after.hour, 6)
        self.assertEqual(before.utcoffset(), timedelta(hours=2))
        self.assertEqual(after.utcoffset(), timedelta(hours=1))

    def test_dispatch_idempotent(self):
        self.s.next_run_at = timezone.now() - timedelta(seconds=5)
        self.s.save()
        dispatch_due()
        dispatch_due()
        self.assertEqual(Job.objects.count(), 1)
        self.assertEqual(
            Job.objects.get().recipients, ["a@example.com", "b@example.com"]
        )

    def test_missed_outside_grace_skipped(self):
        self.s.next_run_at = timezone.now() - timedelta(days=2)
        self.s.save()
        dispatch_due()
        self.assertEqual(Job.objects.get().status, "skipped")

    def test_overlap_skipped(self):
        enqueue_schedule(self.s, timezone.now(), False)
        self.s.next_run_at = timezone.now() - timedelta(seconds=1)
        self.s.save()
        dispatch_due()
        self.assertEqual(Job.objects.filter(status="pending").count(), 1)
        self.assertEqual(Job.objects.filter(status="skipped").count(), 1)

    @patch("reports.artifacts.stream_query", side_effect=fake_stream)
    def test_full_export_and_formula_text(self, mock):
        job = self.job()
        process_job()
        job.refresh_from_db()
        self.assertEqual(job.status, "done")
        self.assertEqual(job.row_count, 501)
        self.assertEqual(len(job.preview), 300)
        with artifact(job, "csv").open(encoding="utf-8-sig") as f:
            rows = list(csv.reader(f, delimiter=";"))
        self.assertEqual(len(rows), 502)
        self.assertEqual(rows[1][1], "'=1+1")
        wb = load_workbook(artifact(job, "xlsx"), read_only=True)
        sheet = wb.active
        self.assertEqual(sum(1 for _ in sheet.rows), 502)
        self.assertEqual(sheet["B2"].data_type, "s")
        wb.close()
        self.client.force_login(self.user)
        for fmt in ("csv", "xlsx"):
            r = self.client.get(reverse("job_download", args=[job.pk, fmt]))
            self.assertEqual(r.status_code, 200)
            r.close()
        self.assertEqual(mock.call_count, 1)

    @patch("reports.artifacts.stream_query", side_effect=fake_stream)
    def test_schedule_to_file_mail_end_to_end(self, mock):
        job = enqueue_schedule(self.s, timezone.now(), False)
        process_job()
        self.assertEqual(Delivery.objects.count(), 2)
        process_mail()
        process_mail()
        self.assertEqual(Delivery.objects.filter(status="test").count(), 2)
        self.assertEqual(len(list((Path(self.temp.name) / "mail").glob("*.eml"))), 2)
        self.assertEqual(mock.call_count, 1)

    def test_query_change_prevents_execution(self):
        j = self.job()
        self.q.sql = "SELECT 1"
        self.q.save()
        with patch("reports.engine.generate") as m:
            process_job()
            m.assert_not_called()
        j.refresh_from_db()
        self.assertEqual(j.status, "failed")

    def test_permission_checked_old_export_and_download(self):
        j = self.job()
        j.status = "done"
        j.save()
        self.client.force_login(self.other)
        self.assertEqual(
            self.client.get(reverse("job_detail", args=[j.pk])).status_code, 403
        )
        group = Group.objects.create(name="Secret")
        self.cat.allowed_groups.add(group)
        self.client.force_login(self.user)
        self.assertEqual(
            self.client.get(reverse("export_csv", args=[self.q.code])).status_code, 403
        )
        self.assertEqual(
            self.client.get(reverse("job_download", args=[j.pk, "csv"])).status_code,
            403,
        )

    def test_double_submit_reuses_pending_job(self):
        self.client.force_login(self.user)
        for _ in range(2):
            self.assertEqual(
                self.client.post(
                    reverse("run_query", args=[self.q.code]), self.params
                ).status_code,
                302,
            )
        self.assertEqual(Job.objects.count(), 1)

    @patch("reports.artifacts.stream_query", side_effect=fake_stream)
    def test_revoke_before_execution(self, mock):
        j = self.job()
        self.user.is_active = False
        self.user.save()
        process_job()
        mock.assert_not_called()
        j.refresh_from_db()
        self.assertEqual(j.status, "failed")

    def test_select_into_rejected(self):
        with self.assertRaises(QueryValidationError):
            validate_select_only("SELECT * INTO Foo FROM Bar")

    def test_uncertain_mail_not_retried(self):
        j = self.job()
        j.status = "done"
        j.save()
        d = Delivery.objects.create(job=j, recipient="a@example.com")
        with patch(
            "reports.engine.send_delivery",
            side_effect=MailFailure("timeout", "uncertain"),
        ) as m:
            process_mail()
            process_mail()
            self.assertEqual(m.call_count, 1)
        d.refresh_from_db()
        self.assertEqual(d.status, "uncertain")

    def test_transient_mail_retry_bounded(self):
        j = self.job()
        j.status = "done"
        j.save()
        d = Delivery.objects.create(job=j, recipient="a@example.com")
        with patch(
            "reports.engine.send_delivery", side_effect=MailFailure("busy", "retry")
        ):
            for _ in range(3):
                process_mail()
                Delivery.objects.filter(pk=d.pk).update(
                    next_attempt_at=timezone.now() - timedelta(seconds=1)
                )
        d.refresh_from_db()
        self.assertEqual(d.status, "failed")
        self.assertEqual(d.attempts, 3)

    @override_settings(
        GRAPH_TENANT_ID="tenant",
        GRAPH_CLIENT_ID="client",
        GRAPH_CLIENT_SECRET="secret",
        GRAPH_SENDER="sender@example.com",
    )
    @patch("reports.mailer.requests.post")
    @patch("reports.mailer.msal.ConfidentialClientApplication")
    def test_graph_adapter(self, auth, post):
        j = self.job()
        j.subject = "Informe"
        j.body = "Datos"
        j.save()
        d = Delivery.objects.create(job=j, recipient="a@example.com")
        path = Path(self.temp.name) / "sample.csv"
        path.write_text("a;b")
        auth.return_value.acquire_token_for_client.return_value = {
            "access_token": "fake"
        }
        post.return_value.status_code = 202
        graph_send(d, path)
        payload = post.call_args.kwargs["json"]
        self.assertEqual(
            payload["message"]["toRecipients"][0]["emailAddress"]["address"],
            "a@example.com",
        )
        self.assertIn("attachments", payload["message"])
        post.return_value.status_code = 503
        with self.assertRaises(MailFailure) as e:
            graph_send(d, path)
        self.assertEqual(e.exception.kind, "uncertain")

    @override_settings(
        SMTP_HOST="relay.example.com", SMTP_TLS=False, SMTP_SSL=False, SMTP_USER=""
    )
    @patch("reports.mailer.smtplib.SMTP")
    def test_smtp_adapter(self, smtp):
        from django.core.mail import EmailMessage

        smtp.return_value.sendmail.return_value = {}
        smtp_send(
            EmailMessage("Asunto", "Texto", "from@example.com", ["to@example.com"])
        )
        smtp.return_value.sendmail.assert_called_once()

    def test_admin_schedule_page_and_post(self):
        admin = User.objects.create_superuser("admin", "admin@example.com", "test")
        self.client.force_login(admin)
        r = self.client.get("/admin/reports/schedule/add/")
        self.assertEqual(r.status_code, 200)
        payload = {
            "name": "Daily",
            "query": self.q.pk,
            "frequency": "daily",
            "every_hours": 1,
            "hour": 6,
            "minute": 0,
            "weekdays": "mon-fri",
            "month_day": "1",
            "period": "yesterday",
            "parameters": "{}",
            "recipients": "a@example.com",
            "output_format": "xlsx",
            "subject": "Informe {query}",
            "body": "Datos {start}",
            "grace_minutes": 60,
            "_save": "Save",
        }
        r = self.client.post("/admin/reports/schedule/add/", payload)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Schedule.objects.get(name="Daily").owner, admin)

    def test_user_pages_render(self):
        j = self.job()
        self.client.force_login(self.user)
        for url in [
            "/",
            reverse("query_detail", args=[self.q.code]),
            reverse("job_list"),
            reverse("job_detail", args=[j.pk]),
        ]:
            self.assertEqual(self.client.get(url).status_code, 200)

    @override_settings(
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
            "externa": {"ENGINE": "mssql"},
        }
    )
    def test_stream_bound_dates_and_batches(self):
        from core.services import stream_query
        from unittest.mock import MagicMock

        cursor = MagicMock()
        cursor.description = [("x",)]
        cursor.fetchmany.side_effect = [[(1,)], [(2,)], []]
        external = MagicMock()
        external.cursor.return_value.__enter__.return_value = cursor
        batches = []
        with patch("core.services.connections", {"externa": external}):
            stream_query(
                self.q, self.user, self.params, lambda cols, rows: batches.append(rows)
            )
        from datetime import date

        self.assertEqual(
            cursor.execute.call_args.args[1], [date(2026, 9, 1), date(2026, 9, 30)]
        )
        self.assertEqual(len(batches), 3)
        param = self.q.params.get(name="Fecha_Fin")
        param.add_one_day = True
        param.save()
        cursor.fetchmany.side_effect = [[]]
        with patch("core.services.connections", {"externa": external}):
            stream_query(self.q, self.user, self.params, lambda *a: None)
        self.assertEqual(cursor.execute.call_args.args[1][-1], date(2026, 10, 1))

    def test_optional_integer_none(self):
        from core.services import cast_param

        param = QueryParam(name="n", param_type="int", required=False)
        self.assertIsNone(cast_param(param, None))

    def test_select_leading_comment_preserved(self):
        validate_select_only("-- informe\n;WITH d AS (SELECT 1 AS n)\nSELECT n FROM d")
