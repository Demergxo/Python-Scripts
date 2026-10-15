import json
from os import access
import re
import time
from dataclasses import dataclass
from typing import Any, List, Dict, Tuple
import datetime as dt

from django.db import connections
from django.utils import timezone
from django.conf import settings
from django.db.models import Q

from .models import Query, QueryRunLog, QueryParam, QueryCategory, UserCategoryAccess

FORBIDDEN_TOKENS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "EXEC",
    "EXECUTE",
    "MERGE",
    "GRANT",
    "REVOKE",
    "CREATE",
    "DECLARE",
    "SET",
    "USE",
    "INTO",
    "OPENROWSET",
    "OPENQUERY",
    "OPENDATASOURCE",
    "BULK",
    "DBCC",
    "BACKUP",
    "RESTORE",
    "WAITFOR",
}

# Quita comentarios iniciales muy básicos y espacios
_leading = re.compile(r"^\s*(?:--[^\r\n]*(?:\r?\n|$)|\s|/\*.*?\*/)*", re.DOTALL)


class QueryValidationError(Exception):
    pass


def get_visible_categories_for_user(user):
    if user.is_superuser:
        return QueryCategory.objects.all()

    user_groups = user.groups.all()

    group_visible = QueryCategory.objects.filter(
        Q(allowed_groups__isnull=True) | Q(allowed_groups__in=user_groups)
    ).distinct()

    extra = QueryCategory.objects.none()
    access = UserCategoryAccess.objects.filter(user=user).first()
    if access:
        extra = access.extra_categories.all()

    return (group_visible | extra).distinct()


def validate_select_only(sql: str) -> None:
    if not sql or not sql.strip():
        raise QueryValidationError("SQL vacío.")

    # Quitar BOM, comentarios iniciales y espacios
    s = sql.lstrip("\ufeff")
    s = _leading.sub("", s).lstrip()

    # Permitir:
    # SELECT ...
    # WITH ...
    # ;WITH ...
    if not re.match(
        r"^(SELECT|WITH|;\s*WITH)\b",
        s,
        flags=re.IGNORECASE,
    ):
        raise QueryValidationError(
            "La consulta debe empezar por SELECT, WITH o ;WITH. "
            f"Inicio detectado: {repr(s[:60])}"
        )

    # El punto y coma inicial de ;WITH está permitido.
    # También permitimos un punto y coma final opcional.
    sql_para_validar = s

    if re.match(r"^;\s*WITH\b", sql_para_validar, flags=re.IGNORECASE):
        sql_para_validar = sql_para_validar[1:].lstrip()

    sql_para_validar = sql_para_validar.rstrip()

    if sql_para_validar.endswith(";"):
        sql_para_validar = sql_para_validar[:-1].rstrip()

    # Cualquier otro punto y coma supone otra sentencia
    if ";" in sql_para_validar:
        raise QueryValidationError("No se permiten múltiples sentencias SQL.")

    # Quitar comentarios antes de comprobar tokens
    sql_sin_comentarios = re.sub(
        r"--[^\r\n]*|/\*.*?\*/",
        " ",
        sql_para_validar,
        flags=re.DOTALL,
    )

    upper = sql_sin_comentarios.upper()

    for token in FORBIDDEN_TOKENS:
        if re.search(rf"\b{re.escape(token)}\b", upper):
            raise QueryValidationError(f"Token prohibido detectado: {token}")


def cast_param(param: QueryParam, raw):
    """
    raw puede venir como:

    - str (si lo mandan como texto)
    - datetime.date (si viene del Datefield del form)
    - int/bool (si viene de campos tipados)
    """

    if param.param_type == QueryParam.ParamType.DATE:
        if raw is None or raw == "":
            # aplica required/default (default en string ISO)
            if param.required and param.default == "":
                raise QueryValidationError(f"Parámetro requerido: {param.name}")
            raw = (param.default or "").strip()

        if isinstance(raw, dt.date):
            return raw  # ya es date

        if isinstance(raw, str):
            raw = raw.strip()
            if raw == "" and not param.required:
                return None  # Se ignora el default si no es obligatorio y está vacío

            try:
                return dt.datetime.fromisoformat(raw).date()
            except:
                raise QueryValidationError(
                    f"Formato de fecha inválido en {param.name}. Debe ser AAAA-MM-DD"
                )

        return raw

    if raw is None:
        raw = ""
    if not isinstance(raw, str):
        if param.param_type == QueryParam.ParamType.INT and isinstance(raw, int):
            return raw
        if param.param_type == QueryParam.ParamType.BOOL and isinstance(raw, bool):
            return raw
        raw = str(raw)
    raw = raw.strip()

    if raw == "":
        if param.required and param.default == "":
            raise QueryValidationError(f"Parámetro requerido: {param.name}")
        raw = (param.default or "").strip()

    if raw == "" and not param.required:
        return None  # Se ignora el default si no es obligatorio y está vacío

    if param.param_type == QueryParam.ParamType.BOOL:
        if raw.lower() in ("1", "true", "t", "si", "sí", "s", "yes", "y", "on"):
            return True
        if raw.lower() in ("0", "false", "f", "no", "n", "off"):
            return False
        raise QueryValidationError(
            f"Valor booleano inválido en {param.name}. Debe ser Sí/No o 1/0"
        )

    if param.param_type == QueryParam.ParamType.INT:
        try:
            return int(raw)
        except (ValueError, TypeError):
            raise QueryValidationError(f"Entero inválido: {param.name}")
    # STR
    return raw


def _add_one_day_if_inclusive_end(param_name: str, value):
    """
    Convención: si el parametro se llama exactamente 'fecha_fin' y es tipo DATE
    el usuario lo entiende como inclusivo. Para que SQL use '< ?', convertimos
    fecha_fin -> fecha_fin + 1 día
    """

    if param_name != "fecha_fin" or value in (None, ""):
        return value

    if isinstance(value, dt.date):
        return value + dt.timedelta(days=1)

    if isinstance(value, str):
        try:
            d = dt.datetime.fromisoformat(value)
            return d + dt.timedelta(days=1)
        except ValueError:
            return value  # No es una fecha válida, devolver tal cual


def assert_query_access(user, q):
    if not user.is_active or not q.is_active:
        raise QueryValidationError("Usuario o consulta desactivados.")
    if not user.is_superuser and (
        not q.category_id
        or not get_visible_categories_for_user(user).filter(pk=q.category_id).exists()
    ):
        raise QueryValidationError("No tienes permisos para esta consulta.")


def stream_query(q, user, raw_params, consume):
    """One SQL execution; callback consumes each batch. No external DB writes."""
    assert_query_access(user, q)
    validate_select_only(q.sql)
    alias = q.database_alias
    if alias not in ("externa", "mahou") or alias not in settings.DATABASES:
        raise QueryValidationError("Conexión de consulta no configurada o desactivada.")
    bound = []
    for p in q.params.all():
        value = cast_param(p, raw_params.get(p.name, ""))
        if (
            p.param_type == QueryParam.ParamType.DATE
            and p.add_one_day
            and value is not None
        ):
            value += dt.timedelta(days=1)
        bound.append(value)
    t0 = time.perf_counter()
    ok = False
    err = ""
    try:
        with connections[alias].cursor() as cursor:
            cursor.execute(q.sql, bound)
            cols = [c[0] for c in cursor.description] if cursor.description else []
            consume(cols, None)
            while True:
                rows = cursor.fetchmany(2000)
                if not rows:
                    break
                consume(cols, rows)
        ok = True
    except Exception as e:
        err = str(e)
        raise
    finally:
        QueryRunLog.objects.create(
            query=q,
            user=user,
            duration_ms=int((time.perf_counter() - t0) * 1000),
            ok=ok,
            params_json=json.dumps(raw_params, ensure_ascii=False, default=str),
            error=err,
        )
