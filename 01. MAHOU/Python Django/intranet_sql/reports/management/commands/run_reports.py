import time
from pathlib import Path
from filelock import FileLock, Timeout
from apscheduler.schedulers.blocking import BlockingScheduler
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from reports.engine import dispatch_due, process_job, process_mail, process_work
from reports.models import Job, Delivery


class Command(BaseCommand):
    help = (
        "Proceso persistente: scheduler, worker o mail. Una instancia por rol/equipo."
    )

    def add_arguments(self, parser):
        parser.add_argument("role", choices=["scheduler", "worker", "mail"])
        parser.add_argument(
            "--once", action="store_true", help="Procesar una iteración (diagnóstico)."
        )

    def handle(self, *args, **options):
        root = Path(settings.REPORT_ROOT)
        root.mkdir(parents=True, exist_ok=True)
        lock = FileLock(str(root / f'.{options["role"]}.lock'))
        try:
            with lock.acquire(timeout=0):
                role = options["role"]
                if role == "worker":
                    from mahou.models import Snapshot
                    Snapshot.objects.filter(status="running").update(status="failed", finished_at=timezone.now(), error="Actualización interrumpida al reiniciar el worker.")
                    Job.objects.filter(status="running").update(
                        status="interrupted",
                        finished_at=timezone.now(),
                        error="Proceso interrumpido. Revisar y ejecutar de nuevo; no se reintenta SQL automáticamente.",
                    )
                elif role == "mail":
                    Delivery.objects.filter(status="sending").update(
                        status="uncertain",
                        error="Proceso interrumpido durante el envío. Verificar en correo antes de reintentar.",
                    )
                fn = {
                    "scheduler": dispatch_due,
                    "worker": process_work,
                    "mail": process_mail,
                }[role]
                if options["once"]:
                    fn()
                    return
                if role == "scheduler":
                    scheduler = BlockingScheduler(timezone="Europe/Madrid")
                    scheduler.add_job(
                        fn,
                        "interval",
                        seconds=10,
                        max_instances=1,
                        coalesce=True,
                        next_run_time=timezone.now(),
                    )
                    try:
                        scheduler.start()
                    except (KeyboardInterrupt, SystemExit):
                        pass
                else:
                    try:
                        while True:
                            if not fn():
                                time.sleep(2)
                    except KeyboardInterrupt:
                        pass
        except Timeout:
            raise CommandError("Ya existe un proceso de este rol usando REPORT_ROOT.")
