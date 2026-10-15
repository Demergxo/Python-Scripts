from reports import views as report_views
from mahou import views as mahou_views
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden

from core.views import home, run_query, export_csv, export_excel, query_detail

def is_admin_group(user):
    return user.is_authenticated and user.is_staff and user.groups.filter(name="Admin").exists()



admin_view =user_passes_test(is_admin_group)(admin.site.login)

urlpatterns = [
    path("mahou/", mahou_views.dashboard, name="mahou_dashboard"),
    path("mahou/actualizar/", mahou_views.refresh, name="mahou_refresh"),
    path("ejecuciones/", report_views.job_list, name="job_list"),
    path("ejecuciones/<uuid:pk>/", report_views.job_detail, name="job_detail"),
    path("ejecuciones/<uuid:pk>/<str:fmt>/", report_views.download, name="job_download"),
    path("admin/", admin.site.urls),

    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("", home, name="home"),

    path("q/<slug:code>/", query_detail, name="query_detail"),
    path("q/<slug:code>/run/", run_query, name="run_query"),

    path("q/<slug:code>/csv/", export_csv, name="export_csv"),
    path("q/<slug:code>/xlsx/", export_excel, name="export_excel"),
]
