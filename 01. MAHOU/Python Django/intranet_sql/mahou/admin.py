from django.contrib import admin
from .models import Snapshot


@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "status",
        "requested_by",
        "requested_at",
        "updated_at",
        "finished_at",
    )
    fields = (
        "status",
        "requested_by",
        "requested_at",
        "started_at",
        "finished_at",
        "updated_at",
        "error",
    )
    readonly_fields = fields

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
