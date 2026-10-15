import calendar
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone as dt_timezone
from string import Formatter
from zoneinfo import ZoneInfo
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.forms import build_query_run_form
from core.services import QueryValidationError

TZ = ZoneInfo("Europe/Madrid")


def fingerprint(q):
    schema = list(
        q.params.values(
            "name", "param_type", "required", "default", "order", "add_one_day"
        )
    )
    return hashlib.sha256(
        json.dumps([q.sql, schema] if q.database_alias == "externa" else [q.sql, schema, q.database_alias], sort_keys=True).encode()
    ).hexdigest()


def parse_recipients(raw):
    values = list(
        dict.fromkeys(v.strip() for v in re.split(r"[,;\s]+", raw) if v.strip())
    )
    if not values:
        raise ValueError("Añade al menos un destinatario.")
    if len(values) > 100:
        raise ValueError("Máximo 100 destinatarios por programación.")
    for value in values:
        try:
            validate_email(value)
        except ValidationError:
            raise ValueError(f"Dirección de correo inválida: {value}")
    return values


def validate_text(text):
    for _, name, spec, conversion in Formatter().parse(text):
        if name is not None and (
            name not in {"query", "start", "end", "job_id"} or spec or conversion
        ):
            raise ValueError(
                "Variables permitidas: {query}, {start}, {end}, {job_id}; sin formatos adicionales."
            )


def trigger_for(s):
    if s.frequency == "once":
        if not s.once_at:
            raise ValueError("Indica una fecha puntual.")
        return DateTrigger(run_date=s.once_at, timezone=TZ)
    if s.frequency == "hours":
        if not s.once_at:
            raise ValueError("Indica el inicio del intervalo en fecha puntual.")
        if s.every_hours < 1:
            raise ValueError("El intervalo debe ser positivo.")
        return IntervalTrigger(hours=s.every_hours, start_date=s.once_at, timezone=TZ)
    args = {"hour": s.hour, "minute": s.minute, "second": 0, "timezone": TZ}
    if s.frequency == "weekly":
        args["day_of_week"] = s.weekdays
    elif s.frequency == "monthly":
        if s.month_day != "last" and not (
            s.month_day.isdigit() and 1 <= int(s.month_day) <= 31
        ):
            raise ValueError("Día mensual: 1 a 31 o last.")
        args["day"] = s.month_day
    elif s.frequency != "daily":
        raise ValueError("Frecuencia desconocida.")
    return CronTrigger(**args)


def next_fire(s, after):
    # after is exclusive; UTC comparison prevents repeated wall-clock hours becoming equal.
    candidate = trigger_for(s).get_next_fire_time(
        None, after + timedelta(microseconds=1)
    )
    if candidate and candidate.astimezone(dt_timezone.utc) <= after.astimezone(
        dt_timezone.utc
    ):
        return None
    return candidate


def clean_parameters(q, raw):
    form = build_query_run_form(q)(raw)
    if not form.is_valid():
        raise QueryValidationError(form.errors.as_text())
    return {
        k: (v.isoformat() if hasattr(v, "isoformat") else v)
        for k, v in form.cleaned_data.items()
    }


def resolve_parameters(s, instant):
    params = dict(s.parameters)
    date = timezone.localtime(instant, TZ).date()
    if s.period != "fixed":
        if s.period == "today":
            start = end = date
        elif s.period == "yesterday":
            start = end = date - timedelta(days=1)
        elif s.period == "previous_week":
            end = date - timedelta(days=date.weekday() + 1)
            start = end - timedelta(days=6)
        elif s.period == "previous_month":
            end = date.replace(day=1) - timedelta(days=1)
            start = end.replace(day=1)
        else:
            raise ValueError("Periodo no válido.")
        names = {
            x.name.lower(): x.name
            for x in s.query.params.all()
            if x.param_type == "date"
        }
        if "fecha_inicio" not in names or "fecha_fin" not in names:
            raise ValueError(
                "El periodo relativo requiere parámetros fecha_inicio y fecha_fin de tipo fecha."
            )
        params[names["fecha_inicio"]] = start.isoformat()
        params[names["fecha_fin"]] = end.isoformat()
    return clean_parameters(s.query, params)
