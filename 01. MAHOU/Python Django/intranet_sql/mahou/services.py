import json
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction, close_old_connections
from django.utils import timezone
from core.models import Query
from core.services import assert_query_access, stream_query, QueryValidationError
from reports.scheduling import fingerprint
from .models import Snapshot
from .data import FIELDS

CODES = ("MAHOU_PANEL", "MAHOU_MUELLES")
log = logging.getLogger(__name__)


def queries_for(user):
    queries = []
    for code in CODES:
        try:
            q = Query.objects.get(code=code)
        except Query.DoesNotExist:
            raise QueryValidationError("El panel Mahou todavía no está instalado.")
        assert_query_access(user, q)
        queries.append(q)
    return queries


def signatures(queries):
    return [fingerprint(q) for q in queries]


def request_refresh(user, interval=60):
    queries_for(user)
    with transaction.atomic():
        snap, _ = Snapshot.objects.select_for_update().get_or_create(pk=1)
        if snap.status in ("pending", "running"):
            return False
        now = timezone.now()
        if snap.requested_at and (now - snap.requested_at).total_seconds() < interval:
            return False
        snap.status = "pending"
        snap.requested_at = now
        snap.requested_by = user
        snap.error = ""
        snap.save(update_fields=["status", "requested_at", "requested_by", "error"])
    return True


def auto_refresh():
    name = settings.MAHOU_AUTO_REFRESH_USER
    if not name:
        return
    try:
        user = get_user_model().objects.get(username=name, is_active=True)
        request_refresh(user, settings.MAHOU_REFRESH_SECONDS)
    except (get_user_model().DoesNotExist, QueryValidationError):
        log.warning("Mahou: responsable automático ausente, inactivo o sin permisos.")


def collect(q, user, required):
    data = []

    def consume(columns, rows):
        if rows is None:
            if not set(required).issubset(columns):
                raise ValueError("Columnas incompatibles con el dashboard Mahou.")
            return
        if len(data) + len(rows) > settings.MAHOU_MAX_ROWS:
            raise ValueError(
                "MAHOU_MAX_ROWS superado; se conserva la última actualización completa."
            )
        data.extend(dict(zip(columns, row)) for row in rows)

    stream_query(q, user, {}, consume)
    return json.loads(json.dumps(data, cls=DjangoJSONEncoder))


def process_refresh():
    close_old_connections()
    with transaction.atomic():
        snap = (
            Snapshot.objects.select_for_update().filter(pk=1, status="pending").first()
        )
        if not snap:
            return False
        snap.status = "running"
        snap.started_at = timezone.now()
        snap.save(update_fields=["status", "started_at"])
    try:
        user = snap.requested_by
        if user is None:
            raise QueryValidationError("Responsable eliminado.")
        queries = queries_for(user)
        hashes = signatures(queries)
        rows = collect(
            queries[0],
            user,
            [f[0] for f in FIELDS]
            + ["1_EstadoFechaTeoricaCarga", "6_EstadoAbiertoCerrado"],
        )
        docks = collect(
            queries[1], user, ["UbicacionCompleta", "NumPalets", "FechaEntradaMin"]
        )
        user.refresh_from_db()
        if signatures(queries_for(user)) != hashes:
            raise QueryValidationError(
                "Consultas modificadas durante la actualización."
            )
        Snapshot.objects.filter(pk=1).update(
            status="done",
            rows=rows,
            docks=docks,
            signatures=hashes,
            updated_at=timezone.now(),
            finished_at=timezone.now(),
            error="",
        )
    except Exception as exc:
        Snapshot.objects.filter(pk=1).update(
            status="failed", finished_at=timezone.now(), error=str(exc)
        )
        log.exception("Falló actualización Mahou")
    finally:
        close_old_connections()
    return True
