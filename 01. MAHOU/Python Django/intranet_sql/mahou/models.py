from django.conf import settings
from django.db import models


class Snapshot(models.Model):
    # One shared, atomically published pair of datasets.
    status = models.CharField(
        max_length=12,
        default="empty",
        choices=[
            ("empty", "Sin datos"),
            ("pending", "En cola"),
            ("running", "Actualizando"),
            ("done", "Actualizado"),
            ("failed", "Fallido"),
        ],
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    requested_at = models.DateTimeField(null=True)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    rows = models.JSONField(default=list)
    docks = models.JSONField(default=list)
    signatures = models.JSONField(default=list)
    error = models.TextField(blank=True)

    class Meta:
        verbose_name = "actualización Mahou"
        verbose_name_plural = "actualizaciones Mahou"
