import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Schedule(models.Model):
    name = models.CharField("Nombre", max_length=160)
    query = models.ForeignKey(
        "core.Query", on_delete=models.PROTECT, verbose_name="Consulta"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Responsable"
    )
    enabled = models.BooleanField("Activa", default=False)
    frequency = models.CharField(
        "Frecuencia",
        max_length=16,
        choices=[
            ("once", "Fecha puntual"),
            ("hours", "Cada N horas"),
            ("daily", "Diaria"),
            ("weekly", "Semanal"),
            ("monthly", "Mensual"),
        ],
        default="daily",
    )
    once_at = models.DateTimeField(
        "Fecha puntual / inicio del intervalo", null=True, blank=True
    )
    every_hours = models.PositiveIntegerField(
        "Cada cuántas horas",
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(8760)],
    )
    hour = models.PositiveSmallIntegerField(
        "Hora", default=6, validators=[MaxValueValidator(23)]
    )
    minute = models.PositiveSmallIntegerField(
        "Minuto", default=0, validators=[MaxValueValidator(59)]
    )
    weekdays = models.CharField(
        "Días semanales",
        max_length=40,
        default="mon-fri",
        help_text="mon-fri o mon,wed,fri; zona Europe/Madrid.",
    )
    month_day = models.CharField(
        "Día del mes",
        max_length=8,
        default="1",
        help_text="1 a 31 o last. Un día inexistente se omite.",
    )
    period = models.CharField(
        "Periodo de datos",
        max_length=20,
        default="yesterday",
        choices=[
            ("fixed", "Parámetros fijos"),
            ("today", "Hoy"),
            ("yesterday", "Ayer"),
            ("previous_week", "Semana anterior (lunes-domingo)"),
            ("previous_month", "Mes anterior"),
        ],
    )
    parameters = models.JSONField(
        "Parámetros fijos",
        default=dict,
        blank=True,
        help_text="Objeto JSON. Las fechas relativas reemplazan Fecha_Inicio/Fecha_Fin o fecha_inicio/fecha_fin.",
    )
    recipients = models.TextField(
        "Destinatarios",
        help_text="Una dirección por línea; también admite comas o punto y coma.",
    )
    output_format = models.CharField(
        "Adjunto",
        max_length=4,
        choices=[("xlsx", "Excel"), ("csv", "CSV")],
        default="xlsx",
    )
    subject = models.CharField(
        "Asunto", max_length=200, default="Informe {query}: {start} — {end}"
    )
    body = models.TextField(
        "Mensaje",
        default="Adjunto el informe {query} del periodo {start} al {end}.\nEjecución: {job_id}",
    )
    send_empty = models.BooleanField("Enviar si no hay filas", default=True)
    grace_minutes = models.PositiveIntegerField(
        "Tolerancia tras un apagado (minutos)",
        default=60,
        validators=[MaxValueValidator(10080)],
    )
    next_run_at = models.DateTimeField(
        "Próxima ejecución", null=True, blank=True, db_index=True, editable=False
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "programación"
        verbose_name_plural = "programaciones"

    def __str__(self):
        return self.name

    def clean(self):
        from .scheduling import (
            trigger_for,
            parse_recipients,
            validate_text,
            resolve_parameters,
        )
        from core.services import (
            assert_query_access,
            QueryValidationError,
            validate_select_only,
        )
        from django.utils import timezone

        try:
            if not isinstance(self.parameters, dict):
                raise ValueError("Parámetros debe ser un objeto JSON.")
            trigger_for(self)
            parse_recipients(self.recipients)
            validate_text(self.subject)
            validate_text(self.body)
            if "\n" in self.subject or "\r" in self.subject:
                raise ValueError("El asunto no admite saltos de línea.")
            if self.query_id and self.owner_id:
                assert_query_access(self.owner, self.query)
                if not self.owner.is_staff:
                    raise ValueError(
                        "El responsable debe tener acceso al administrador."
                    )
                validate_select_only(self.query.sql)
                resolve_parameters(self, self.once_at or timezone.now())
        except (ValueError, QueryValidationError) as e:
            raise ValidationError(str(e))


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    query = models.ForeignKey("core.Query", on_delete=models.PROTECT)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    schedule = models.ForeignKey(
        Schedule, on_delete=models.SET_NULL, null=True, blank=True
    )
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sql_hash = models.CharField(max_length=64)
    parameters = models.JSONField(default=dict)
    status = models.CharField(
        max_length=16,
        default="pending",
        choices=[
            ("pending", "Pendiente"),
            ("running", "Ejecutando"),
            ("done", "Terminado"),
            ("failed", "Fallido"),
            ("interrupted", "Interrumpido"),
            ("skipped", "Omitido"),
        ],
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    row_count = models.PositiveIntegerField(default=0)
    columns = models.JSONField(default=list)
    preview = models.JSONField(default=list)
    error = models.TextField(blank=True)
    duration_ms = models.PositiveIntegerField(default=0)
    recipients = models.JSONField(default=list)
    subject = models.CharField(max_length=240, blank=True)
    body = models.TextField(blank=True)
    output_format = models.CharField(max_length=4, default="xlsx")
    send_empty = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["schedule", "scheduled_for"], name="unique_schedule_occurrence"
            )
        ]
        ordering = ["-created_at"]
        verbose_name = "ejecución"
        verbose_name_plural = "ejecuciones"

    def __str__(self):
        return f"{self.query.code} · {self.get_status_display()} · {self.id}"


class Delivery(models.Model):
    job = models.ForeignKey(Job, on_delete=models.PROTECT, related_name="deliveries")
    recipient = models.EmailField()
    status = models.CharField(
        max_length=16,
        default="pending",
        db_index=True,
        choices=[
            ("pending", "Pendiente"),
            ("sending", "Enviando"),
            ("accepted", "Aceptado por servidor"),
            ("test", "Guardado de prueba"),
            ("failed", "Fallido"),
            ("uncertain", "Incierto: revisar"),
        ],
    )
    attempts = models.PositiveIntegerField(default=0)
    next_attempt_at = models.DateTimeField(null=True, blank=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    provider = models.CharField(max_length=16, blank=True)
    error = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["job", "recipient"], name="unique_job_recipient"
            )
        ]
        verbose_name = "envío"
        verbose_name_plural = "envíos"

    def __str__(self):
        return f"{self.job_id} · {self.recipient} · {self.get_status_display()}"
