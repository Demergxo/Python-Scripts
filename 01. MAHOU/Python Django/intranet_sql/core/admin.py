from django.contrib import admin
from .models import Query, QueryParam, QueryRunLog, QueryCategory
from .models import QueryCategory, UserCategoryAccess


admin.site.site_header = "Panel de Administración"
admin.site.site_title = "Administración"
admin.site.index_title = "Gestión del sistema"

class QueryParamInline(admin.TabularInline):
    model = QueryParam
    extra = 0


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    search_fields = ("code", "name")
    list_filter = ("is_active", "category")
    inlines = [QueryParamInline]


@admin.register(QueryRunLog)
class QueryRunLogAdmin(admin.ModelAdmin):
    list_display = ("ran_at", "user", "query", "ok", "duration_ms")
    list_filter = ("ok", "query")
    search_fields = ("user__username", "query__code", "query__name")

@admin.register(QueryCategory)
class QueryCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    ordering = ("order", "name")
    filter_horizontal = ("allowed_groups",)

@admin.register(UserCategoryAccess)
class UserCategoryAccessAdmin(admin.ModelAdmin):
    list_display = ("user",)
    filter_horizontal = ("extra_categories",)
    search_fields = ("user__username",)


