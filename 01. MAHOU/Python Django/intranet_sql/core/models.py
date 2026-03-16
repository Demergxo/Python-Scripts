from django.conf import settings
from django.db import models
from django.contrib.auth.models import Group

class QueryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0)

    allowed_groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="allowed_categories",
        help_text="Grupos que pueden ver esta categoría. Si está vacío, la ve todo el mundo.",
    )

    class Meta:
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name


class Query(models.Model):
    code = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    sql = models.TextField(help_text="Usa placeholders '%s' (estilo Django). Ej: WHERE campo >= %s AND campo < %s")
    is_active = models.BooleanField(default=True)

    category = models.ForeignKey(
        QueryCategory,
        on_delete=models.PROTECT,
        related_name="queries",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class QueryParam(models.Model):
    class ParamType(models.TextChoices):
        INT = "int", "Entero"
        STR = "str", "Texto"
        DATE = "date", "Fecha"
        BOOL = "bool", "Booleano"

    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name="params")
    order = models.PositiveIntegerField(help_text="Orden posicional para '?'")
    name = models.SlugField(max_length=64)
    label = models.CharField(max_length=120)
    param_type = models.CharField(max_length=10, choices=ParamType.choices)
    required = models.BooleanField(default=False)
    default = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = [("query", "order"), ("query", "name")]
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.query.code}[{self.order}] {self.name} ({self.param_type})"


class QueryRunLog(models.Model):
    query = models.ForeignKey(Query, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    ran_at = models.DateTimeField(auto_now_add=True)
    duration_ms = models.PositiveIntegerField()
    ok = models.BooleanField(default=True)
    params_json = models.TextField(blank=True)
    error = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.ran_at:%Y-%m-%d %H:%M:%S} {self.user} {self.query.code} ok={self.ok}"

class UserCategoryAccess(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    extra_categories = models.ManyToManyField(
        QueryCategory,
        blank=True,
        related_name="extra_users",
        help_text="Categorías adicionales para este usuario (además de sus grupos).",
    )

    def __str__(self) -> str:
        return f"Extra categories for {self.user}"
