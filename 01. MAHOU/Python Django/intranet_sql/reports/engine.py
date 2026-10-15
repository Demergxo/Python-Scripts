import logging
import time
from datetime import timedelta
from django.conf import settings
from django.db import transaction, close_old_connections
from django.utils import timezone
from core.services import assert_query_access, QueryValidationError
from .models import Schedule, Job, Delivery
from .scheduling import (
    fingerprint,
    resolve_parameters,
    parse_recipients,
    next_fire,
    clean_parameters,
    validate_text,
)
from .artifacts import generate
from .mailer import send_delivery, MailFailure

log = logging.getLogger(__name__)


def create_job(q, owner, params, **extra):
    assert_query_access(owner, q)
    params = clean_parameters(q, params)
    return Job.objects.create(
        query=q, owner=owner, parameters=params, sql_hash=fingerprint(q), **extra
    )


def enqueue_schedule(s, when, scheduled=True):
    # Caller holds a short transaction; SQL is never executed under this lock.
    s.full_clean()
    params = resolve_parameters(s, when)
    job = create_job(
        s.query,
        s.owner,
        params,
        schedule=s,
        scheduled_for=when if scheduled else None,
        recipients=parse_recipients(s.recipients),
        output_format=s.output_format,
        send_empty=s.send_empty,
    )
    dates = {k.lower(): v for k, v in params.items()}
    values = {
        "query": s.query.code,
        "start": dates.get("fecha_inicio", ""),
        "end": dates.get("fecha_fin", ""),
        "job_id": str(job.pk),
    }
    job.subject = s.subject.format(**values)
    job.body = s.body.format(**values)
    job.save(update_fields=["subject", "body"])
    return job


def dispatch_due():
    from mahou.services import auto_refresh
    auto_refresh()
    close_old_connections()
    now = timezone.now()
    ids = list(
        Schedule.objects.filter(enabled=True, next_run_at__lte=now).values_list(
            "pk", flat=True
        )
    )
    for pk in ids:
        with transaction.atomic():
            s = (
                Schedule.objects.select_for_update()
                .select_related("query", "owner")
                .get(pk=pk)
            )
            if not s.enabled or not s.next_run_at or s.next_run_at > now:
                continue
            due = s.next_run_at
            if not Job.objects.filter(schedule=s, scheduled_for=due).exists():
                reason = ""
                if (now - due).total_seconds() > s.grace_minutes * 60:
                    reason = "Horario perdido: se superó la tolerancia tras la parada."
                elif Job.objects.filter(
                    schedule=s, status__in=["pending", "running"]
                ).exists():
                    reason = "Omitida por solapamiento con otra ejecución de esta programación."
                if reason:
                    Job.objects.create(
                        query=s.query,
                        owner=s.owner,
                        schedule=s,
                        scheduled_for=due,
                        sql_hash="",
                        status="skipped",
                        error=reason,
                        finished_at=now,
                    )
                else:
                    try:
                        with transaction.atomic():
                            enqueue_schedule(s, due)
                    except Exception as e:
                        Job.objects.create(
                            query=s.query,
                            owner=s.owner,
                            schedule=s,
                            scheduled_for=due,
                            sql_hash="",
                            status="failed",
                            error=str(e),
                            finished_at=now,
                        )
            # One overdue occurrence at most; no burst replay after downtime.
            s.next_run_at = next_fire(s, now)
            if s.next_run_at is None:
                s.enabled = False
            s.save(update_fields=["next_run_at", "enabled"])
    close_old_connections()


def process_job():
    close_old_connections()
    with transaction.atomic():
        job = (
            Job.objects.select_for_update()
            .filter(status="pending")
            .order_by("created_at")
            .first()
        )
        if job is None:
            return False
        job.status = "running"
        job.started_at = timezone.now()
        job.save(update_fields=["status", "started_at"])
    started = time.perf_counter()
    try:
        assert_query_access(job.owner, job.query)
        if job.schedule_id and not job.owner.is_staff:
            raise QueryValidationError("Responsable sin acceso de administración.")
        if fingerprint(job.query) != job.sql_hash:
            raise QueryValidationError(
                "SQL o parámetros modificados tras encolar; crea una ejecución nueva."
            )
        cols, preview, count = generate(job)
        # Do not publish results if permissions were revoked while SQL ran.
        job.owner.refresh_from_db()
        job.query.refresh_from_db()
        assert_query_access(job.owner, job.query)
        with transaction.atomic():
            job.status = "done"
            job.columns = cols
            job.preview = preview
            job.row_count = count
            job.finished_at = timezone.now()
            job.duration_ms = int((time.perf_counter() - started) * 1000)
            job.save()
            if count or job.send_empty:
                Delivery.objects.bulk_create(
                    [Delivery(job=job, recipient=r) for r in job.recipients]
                )
    except Exception as e:
        Job.objects.filter(pk=job.pk).update(
            status="failed",
            error=str(e),
            finished_at=timezone.now(),
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
        log.exception("Falló ejecución %s", job.pk)
    finally:
        close_old_connections()
    return True


def process_mail():
    close_old_connections()
    now = timezone.now()
    with transaction.atomic():
        from django.db.models import Q

        d = (
            Delivery.objects.select_for_update()
            .filter(status="pending")
            .filter(Q(next_attempt_at__isnull=True) | Q(next_attempt_at__lte=now))
            .order_by("pk")
            .first()
        )
        if d is None:
            return False
        d.status = "sending"
        d.attempts += 1
        d.provider = settings.MAIL_PROVIDER
        d.save()
    try:
        assert_query_access(d.job.owner, d.job.query)
        if d.job.status != "done":
            raise MailFailure("La ejecución no está terminada.")
        if d.job.schedule_id and not d.job.owner.is_staff:
            raise MailFailure("Responsable sin acceso de administración.")
        d.status = send_delivery(d)
        d.error = ""
        d.next_attempt_at = None
    except MailFailure as e:
        d.error = str(e)
        if e.kind == "retry" and d.attempts < settings.MAIL_MAX_ATTEMPTS:
            d.status = "pending"
            d.next_attempt_at = now + timedelta(
                seconds=max(e.delay, 60 * 2**d.attempts)
            )
        else:
            d.status = "uncertain" if e.kind == "uncertain" else "failed"
    except QueryValidationError as e:
        d.status = "failed"
        d.error = str(e)
    except Exception:
        # Unknown error could be after submission; manual review is safer than duplicate mail.
        d.status = "uncertain"
        d.error = "Error no clasificado; revisar antes de reenviar."
        log.exception("Envío %s", d.pk)
    d.save()
    close_old_connections()
    return True


def process_work():
    from mahou.services import process_refresh
    refreshed = process_refresh()
    processed = process_job()
    return refreshed or processed
