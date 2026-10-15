from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from core.views import context
from core.services import (
    assert_query_access,
    QueryValidationError,
    get_visible_categories_for_user,
)
from .models import Job
from .artifacts import artifact


def accessible(request, pk):
    job = get_object_or_404(Job.objects.select_related("query", "owner"), pk=pk)
    manager = request.user.is_staff and request.user.has_perm("reports.view_job")
    if job.owner_id != request.user.pk and not manager:
        raise PermissionDenied
    try:
        assert_query_access(request.user, job.query)
    except QueryValidationError:
        raise PermissionDenied
    return job


@login_required
def job_list(request):
    jobs = Job.objects.filter(owner=request.user)
    if not request.user.is_superuser:
        jobs = jobs.filter(
            query__category__in=get_visible_categories_for_user(request.user),
            query__is_active=True,
        )
    page = Paginator(jobs.select_related("query"), 30).get_page(request.GET.get("page"))
    return render(request, "reports/list.html", {**context(request.user), "page": page})


@login_required
def job_detail(request, pk):
    job = accessible(request, pk)
    return render(
        request,
        "reports/detail.html",
        {
            **context(request.user),
            "job": job,
            "cols": job.columns,
            "rows": job.preview,
            "deliveries": job.deliveries.all(),
            "show_error": request.user.is_staff,
            "refresh": job.status in ("pending", "running"),
        },
    )


@login_required
def download(request, pk, fmt):
    job = accessible(request, pk)
    if job.status != "done" or fmt not in ("csv", "xlsx"):
        raise Http404
    path = artifact(job, fmt)
    if not path.exists():
        raise Http404("El archivo ya no está disponible.")
    return FileResponse(path.open("rb"), as_attachment=True, filename=path.name)
