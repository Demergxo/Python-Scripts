import csv
from datetime import datetime
from pathlib import Path
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from django.conf import settings
from core.services import stream_query


def directory(job):
    return Path(settings.REPORT_ROOT) / str(job.pk)


def artifact(job, fmt):
    if fmt not in ("csv", "xlsx"):
        raise ValueError("Formato inválido")
    return directory(job) / f"{job.query.code}_{job.pk}.{fmt}"


def csv_value(value):
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def excel_value(ws, value):
    if isinstance(value, datetime) and value.tzinfo:
        value = value.isoformat()
    if isinstance(value, str):
        cell = WriteOnlyCell(ws, value=value)
        cell.data_type = "s"
        return cell
    return value


def generate(job):
    root = directory(job)
    root.mkdir(parents=True, exist_ok=True)
    csvpath = artifact(job, "csv")
    xlpath = artifact(job, "xlsx")
    csvtmp = csvpath.with_suffix(".csv.tmp")
    xltmp = xlpath.with_suffix(".xlsx.tmp")
    wb = Workbook(write_only=True)
    ws = wb.create_sheet("Resultados")
    count = 0
    preview = []
    columns = []
    try:
        with csvtmp.open("w", encoding="utf-8-sig", newline="") as fp:
            writer = csv.writer(fp, delimiter=";")

            def consume(cols, rows):
                nonlocal count, columns
                if rows is None:
                    columns = cols
                    writer.writerow([csv_value(x) for x in cols])
                    ws.append([excel_value(ws, x) for x in cols])
                    return
                for row in rows:
                    count += 1
                    if count > settings.REPORT_MAX_ROWS:
                        raise ValueError(
                            "Se supera REPORT_MAX_ROWS; acota el periodo. No se publicará un archivo parcial."
                        )
                    writer.writerow([csv_value(x) for x in row])
                    ws.append([excel_value(ws, x) for x in row])
                    if len(preview) < 300:
                        preview.append([None if x is None else str(x) for x in row])

            stream_query(job.query, job.owner, job.parameters, consume)
        wb.save(xltmp)
        csvtmp.replace(csvpath)
        xltmp.replace(xlpath)
        return columns, preview, count
    finally:
        wb.close()
        for path in (csvtmp, xltmp):
            path.unlink(missing_ok=True)
