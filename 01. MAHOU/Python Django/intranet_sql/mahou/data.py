"""XGA columns and presentation contract from PANEL!C:T, excluding Altia."""

from collections import Counter
from decimal import Decimal, InvalidOperation

FIELDS = [
    ("2_Albaran", "Albarán", "text"),
    ("3_ID_Extraccion", "Extracción", "text"),
    ("4_ID_Expediente", "Expediente", "text"),
    ("7_TipoEstadoConvertido", "Estado", "state"),
    ("5_FechaTeoricaCargaDoc", "Fecha XGA carga", "date"),
    ("13_NombreDireccion", "Cliente", "text"),
    ("15_RutaReparto", "Transporte", "text"),
    ("21_PorcTotalPalets", "% Palet", "percent"),
    ("23_PorcPickingCajas", "% PickCaj", "percent"),
    ("16_PaletsCompletos", "PalComp", "number"),
    ("22_PickingCajas", "PickCajas", "number"),
    ("20_PendientePalets", "PalPend", "number"),
    ("24_PickPend", "PickPend", "number"),
    ("34_SSCCPendientesCarga", "Por cargar", "number"),
    ("33_SSCCCargados", "Cargado", "number"),
    ("31_UbicacionesPendientesCarga", "Muelle XGA", "text"),
    ("8_FechaHoraEstado10", "Fecha integración", "date"),
    ("14_Comentario", "Instrucciones", "text"),
]
PERIODS = ["Hoy", "Ayer", "Backlog", "Mañana", "Pasado mañana", "Futuro"]
STATES = ["10", "20", "20-INC", "30", "40"]


def number(value):
    if value in (None, ""):
        return None
    try:
        v = Decimal(str(value).strip())
        return v if v.is_finite() else None
    except InvalidOperation:
        return None


def format_number(value):
    v = number(value)
    if v is None:
        return "—"
    return (
        f"{v:,.1f}".rstrip("0")
        .rstrip(".")
        .replace(",", "_")
        .replace(".", ",")
        .replace("_", ".")
    )


def display(value, kind):
    if value in (None, ""):
        return "—"
    if kind in ("number", "percent"):
        return format_number(value) + (
            " %" if kind == "percent" and number(value) is not None else ""
        )
    if kind == "date":
        from datetime import datetime

        try:
            # XGA timestamps are retained as returned by the source.
            return datetime.fromisoformat(str(value)).strftime("%d/%m/%Y %H:%M")
        except ValueError:
            return str(value)
    return str(value)


def filtered(rows, values):
    result = []
    for row in rows:
        if (
            values.get("period")
            and row.get("1_EstadoFechaTeoricaCarga") != values["period"]
        ):
            continue
        if (
            values.get("status")
            and row.get("6_EstadoAbiertoCerrado") != values["status"]
        ):
            continue
        if values.get("state") and row.get("7_TipoEstadoConvertido") != values["state"]:
            continue
        if any(
            values.get(k)
            and values[k].casefold() not in str(row.get(col) or "").casefold()
            for k, col in [
                ("albaran", "2_Albaran"),
                ("extraccion", "3_ID_Extraccion"),
                ("expediente", "4_ID_Expediente"),
                ("cliente", "13_NombreDireccion"),
                ("muelle", "31_UbicacionesPendientesCarga"),
            ]
        ):
            continue
        result.append(row)
    return sorted(
        result,
        key=lambda r: (
            not bool(r.get("5_FechaTeoricaCargaDoc")),
            str(r.get("5_FechaTeoricaCargaDoc") or ""),
            str(r.get("2_Albaran") or ""),
        ),
    )


def present(rows):
    result = []
    for row in rows:
        cells = []
        for key, label, kind in FIELDS:
            value = row.get(key)
            css = ""
            if kind == "state":
                css = "state-" + str(value).lower()
            elif kind == "percent" and number(value) is not None:
                css = "good" if number(value) >= 100 else ""
            elif (
                key in ("20_PendientePalets", "24_PickPend", "34_SSCCPendientesCarga")
                and number(value) is not None
            ):
                css = "pending-value" if number(value) > 0 else "good"
            elif key == "15_RutaReparto" and "_ERROR(" in str(value):
                css = "bad"
            cells.append(
                {
                    "value": display(value, kind),
                    "class": css,
                    "numeric": kind in ("number", "percent"),
                }
            )
        result.append(cells)
    return result


def summary(rows):
    states = Counter(str(r.get("7_TipoEstadoConvertido") or "Sin estado") for r in rows)
    cards = [
        ("Filas", str(len(rows))),
        (
            "Albaranes distintos",
            str(
                len(
                    {
                        str(r["2_Albaran"])
                        for r in rows
                        if r.get("2_Albaran") not in (None, "")
                    }
                )
            ),
        ),
        ("Incidencias 20-INC", str(states["20-INC"])),
    ]
    return cards, [
        {
            "name": s,
            "count": states[s],
            "width": 100 * states[s] / max(len(rows), 1),
            "css": "state-" + s.lower(),
        }
        for s in STATES
    ]


def dock_groups(rows):
    groups = {}
    for r in rows:
        for name in dict.fromkeys(
            x.strip()
            for x in str(r.get("31_UbicacionesPendientesCarga") or "").split("|")
            if x.strip()
        ):
            groups.setdefault(name, []).append(r)
    return [
        {"name": name, "rows": present(rs), "count": len(rs)}
        for name, rs in sorted(groups.items())
    ]


def occupancy(rows):
    result = []
    for r in rows:
        n = number(r.get("NumPalets"))
        result.append(
            {
                "name": r.get("UbicacionCompleta") or "Sin ubicación",
                "count": display(r.get("NumPalets"), "number"),
                "date": display(r.get("FechaEntradaMin"), "date"),
                "status": (
                    "Sin dato" if n is None else ("Ocupado" if n > 0 else "Libre")
                ),
                "css": "unknown" if n is None else ("occupied" if n > 0 else "free"),
            }
        )
    return sorted(result, key=lambda r: r["name"])
