from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from .models import Query
from .forms import build_query_run_form
from .services import (
    get_visible_categories_for_user,
    assert_query_access,
    QueryValidationError,
)


def context(user):
    return {
        "categories": get_visible_categories_for_user(user).order_by("order", "name"),
        "is_admin": user.is_staff,
        "sidebar_mode": "links",
    }


def allowed_query(user, code):
    q = get_object_or_404(Query, code=code, is_active=True)
    try:
        assert_query_access(user, q)
    except QueryValidationError as e:
        raise PermissionDenied(str(e))
    return q


@login_required
def home(request):
    data = context(request.user)
    queries = (
        Query.objects.filter(is_active=True, category__in=data["categories"])
        .select_related("category")
        .order_by("name")
    )
    grouped = {c: [] for c in data["categories"]}
    for q in queries:
        grouped[q.category].append(q)
    data.update(grouped=grouped, uncategorized=[], sidebar_mode="workspace")
    return render(request, "workspace.html", data)


@login_required
def query_detail(request, code):
    q = allowed_query(request.user, code)
    return render(
        request,
        "query_detail.html",
        {**context(request.user), "query": q, "form": build_query_run_form(q)()},
    )


@login_required
def run_query(request, code):
    from reports.engine import create_job
    from reports.models import Job
    from reports.scheduling import fingerprint, clean_parameters

    q = allowed_query(request.user, code)
    form = build_query_run_form(q)(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        params = clean_parameters(q, form.cleaned_data)
        # Prevent double-clicks creating parallel work for the same user and parameters.
        with transaction.atomic():
            pending = Job.objects.filter(
                owner=request.user,
                query=q,
                schedule__isnull=True,
                status__in=["pending", "running"],
                sql_hash=fingerprint(q),
            )
            job = next((j for j in pending if j.parameters == params), None)
            if job is None:
                job = create_job(q, request.user, params)
        return redirect("job_detail", pk=job.pk)
    return render(
        request,
        "query_detail.html",
        {**context(request.user), "query": q, "form": form},
    )


@login_required
def export_csv(request, code):
    # Old bookmarks still check permissions, but GET never launches a query.
    allowed_query(request.user, code)
    return (
        run_query(request, code)
        if request.method == "POST"
        else redirect("query_detail", code=code)
    )


@login_required
def export_excel(request, code):
    allowed_query(request.user, code)
    return (
        run_query(request, code)
        if request.method == "POST"
        else redirect("query_detail", code=code)
    )
