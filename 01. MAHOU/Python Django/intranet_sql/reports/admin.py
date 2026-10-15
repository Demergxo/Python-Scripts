from django.contrib import admin, messages
from django.db import transaction
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from core.models import Query
from core.services import get_visible_categories_for_user
from .models import Schedule, Job, Delivery
from .scheduling import next_fire
from .engine import enqueue_schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "query",
        "enabled",
        "frequency",
        "period",
        "next_run_at",
        "owner",
    )
    list_filter = ("enabled", "frequency", "query")
    search_fields = ("name", "query__code")
    readonly_fields = ("owner", "next_run_at", "updated_at")
    actions = ["pause", "run_now"]
    fieldsets = (
        ("Informe", {"fields": ("name", "query", "owner", "enabled")}),
        (
            "Calendario · Europe/Madrid",
            {
                "fields": (
                    "frequency",
                    "once_at",
                    "every_hours",
                    "hour",
                    "minute",
                    "weekdays",
                    "month_day",
                    "grace_minutes",
                    "next_run_at",
                )
            },
        ),
        ("Datos", {"fields": ("period", "parameters")}),
        (
            "Correo",
            {
                "fields": (
                    "recipients",
                    "output_format",
                    "subject",
                    "body",
                    "send_empty",
                )
            },
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(owner=request.user)

    def get_form(self, request, obj=None, **kwargs):
        Form = super().get_form(request, obj, **kwargs)

        class OwnedForm(Form):
            def __init__(self, *a, **kw):
                super().__init__(*a, **kw)
                if not self.instance.owner_id:
                    self.instance.owner = request.user

        return OwnedForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "query":
            qs = Query.objects.filter(is_active=True)
            if not request.user.is_superuser:
                qs = qs.filter(
                    category__in=get_visible_categories_for_user(request.user)
                )
            kwargs["queryset"] = qs
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.owner_id:
            obj.owner = request.user
        obj.next_run_at = next_fire(obj, timezone.now()) if obj.enabled else None
        if obj.enabled and obj.next_run_at is None:
            obj.enabled = False
            self.message_user(
                request,
                "No quedan fechas futuras: programación guardada en pausa.",
                messages.WARNING,
            )
        super().save_model(request, obj, form, change)

    @admin.action(
        description="Pausar programaciones (no cancela trabajos ya creados)",
        permissions=["change"],
    )
    def pause(self, request, queryset):
        queryset.update(enabled=False, next_run_at=None)

    @admin.action(
        description="Ejecutar ahora y enviar a los destinatarios configurados",
        permissions=["change"],
    )
    def run_now(self, request, queryset):
        for s in queryset:
            try:
                with transaction.atomic():
                    if Job.objects.filter(
                        schedule=s, status__in=["pending", "running"]
                    ).exists():
                        self.message_user(
                            request,
                            f"{s}: ya tiene un trabajo pendiente.",
                            messages.WARNING,
                        )
                        continue
                    enqueue_schedule(s, timezone.now(), scheduled=False)
                self.message_user(request, f"{s}: encolada.")
            except Exception as e:
                self.message_user(request, str(e), messages.ERROR)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "query",
        "owner",
        "status",
        "row_count",
        "duration_ms",
        "created_at",
        "result_link",
    )
    list_filter = ("status", "query")
    exclude = ("preview",)
    readonly_fields = tuple(f.name for f in Job._meta.fields)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs
            if request.user.is_superuser
            else qs.filter(
                owner=request.user,
                query__category__in=get_visible_categories_for_user(request.user),
            )
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def result_link(self, obj):
        return format_html(
            '<a href="{}">Ver resultado</a>', reverse("job_detail", args=[obj.pk])
        )

    result_link.short_description = "Resultado"


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "job",
        "recipient",
        "status",
        "provider",
        "attempts",
        "updated_at",
    )
    list_filter = ("status", "provider")
    readonly_fields = tuple(f.name for f in Delivery._meta.fields)
    actions = ["retry_failed", "authorize_resend"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs
            if request.user.is_superuser
            else qs.filter(
                job__owner=request.user,
                job__query__category__in=get_visible_categories_for_user(request.user),
            )
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(
        description="Reintentar envíos fallidos (sin ejecutar SQL)",
        permissions=["change"],
    )
    def retry_failed(self, request, queryset):
        n = queryset.filter(status="failed").update(
            status="pending",
            attempts=0,
            next_attempt_at=None,
            error="Reintento manual autorizado por " + request.user.get_username(),
        )
        self.message_user(request, f"{n} envíos pendientes.")

    @admin.action(
        description="Confirmo reenvío: puede duplicar correos aceptados o inciertos",
        permissions=["change"],
    )
    def authorize_resend(self, request, queryset):
        n = queryset.filter(status__in=["accepted", "uncertain", "test"]).update(
            status="pending",
            attempts=0,
            next_attempt_at=None,
            error="Reenvío manual autorizado por " + request.user.get_username(),
        )
        self.message_user(
            request,
            f"{n} reenvíos pendientes; se usará el archivo existente.",
            messages.WARNING,
        )
