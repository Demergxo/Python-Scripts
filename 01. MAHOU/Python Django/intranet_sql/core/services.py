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
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "EXEC", "EXECUTE", "MERGE", "GRANT", "REVOKE", "CREATE",
    "DECLARE", "SET", "USE",
}

# Quita comentarios iniciales muy básicos y espacios
_leading = re.compile(r"^\s*(?:--.*\n|\s|/\*.*?\*/)*", re.DOTALL)


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

    s = _leading.sub("", sql).lstrip()

    # 1) Debe empezar por SELECT
    if not re.match(r"(?i)^select\b", s):
        raise QueryValidationError("La consulta debe empezar por SELECT.")

    # 2) Bloqueo tokens peligrosos (por palabra)
    upper = sql.upper()
    for tok in FORBIDDEN_TOKENS:
        if re.search(rf"\b{re.escape(tok)}\b", upper):
            raise QueryValidationError(f"Token prohibido detectado: {tok}")

    # 3) Opcional: bloquear ';' para evitar múltiples statements
    if ";" in sql:
        raise QueryValidationError("No se permite ';' en la consulta.")


def cast_param(param: QueryParam, raw):
    """
    raw puede venir como:

    - str (si lo mandan como texto)
    - datetime.date (si viene del Datefield del form)
    - int/bool (si viene de campos tipados)
    """

    if param.param_type == QueryParam.ParamType.DATE:
        if raw is None or raw == "":
            #aplica required/default (default en string ISO)
            if param.required and param.default == "":
                raise QueryValidationError(f"Parámetro requerido: {param.name}")
            raw = (param.default or "").strip()

        if isinstance(raw, dt.date):
            return raw  # ya es date
        
        if isinstance(raw, str):
            raw = raw.strip()
            if raw == "" and not param.required:
                return None # Se ignora el default si no es obligatorio y está vacío
            
            try:
                return dt.datetime.fromisoformat(raw).date()
            except:
                raise QueryValidationError(f"Formato de fecha inválido en {param.name}. Debe ser AAAA-MM-DD")
            
        return raw
    
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
        return None # Se ignora el default si no es obligatorio y está vacío
    
    if param.param_type == QueryParam.ParamType.BOOL:
        if raw.lower() in ("1", "true", "t", "si", "sí", "s", "yes", "y", "on"):
            return True
        if raw.lower() in ("0", "false", "f", "no", "n", "off"):
            return False
        raise QueryValidationError(f"Valor booleano inválido en {param.name}. Debe ser Sí/No o 1/0")
    
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
            return value # No es una fecha válida, devolver tal cual


def execute_query(code: str, user, raw_params: Dict[str, str]) -> Tuple[List[str], List[Tuple[Any, ...]]]:
    if "externa" not in settings.DATABASES:
        raise QueryValidationError("BD externa desactivada en este entorno.")
    q = Query.objects.get(code=code, is_active=True)

    validate_select_only(q.sql)

    params_def = list(q.params.all()) #type:ignore
    bound_params: List[Any] = []

    for p in params_def:
        v = cast_param(p, raw_params.get(p.name, ""))
        if p.param_type == QueryParam.ParamType.DATE:
            v = _add_one_day_if_inclusive_end(p.name, v)
        bound_params.append(v)

    # pyodbc: si pasas None, suele mapear a NULL bien
    t0 = time.perf_counter()
    ok = True
    err = ""
    rows: List[Tuple[Any, ...]] = []
    cols: List[str] = []

    try:
        with connections["externa"].cursor() as cursor:
            cursor.execute(q.sql, bound_params)
            cols = [c[0] for c in cursor.description] if cursor.description else []
            rows = cursor.fetchmany(300)
            #rows = cursor.fetchall()
    except Exception as e:
        ok = False
        err = str(e)
        raise
    finally:
        dt_ms = int((time.perf_counter() - t0) * 1000)
        QueryRunLog.objects.create(
            query=q,
            user=user,
            duration_ms=dt_ms,
            ok=ok,
            params_json=json.dumps(raw_params, ensure_ascii=False, default=str),
            error=err,
        )

    return cols, rows
