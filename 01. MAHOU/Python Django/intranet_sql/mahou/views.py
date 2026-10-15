import csv
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.utils import timezone
from core.views import context
from core.services import QueryValidationError
from reports.artifacts import csv_value
from .models import Snapshot
from .services import queries_for, signatures, request_refresh
from .forms import Filters
from .data import FIELDS, filtered, present, summary, dock_groups, occupancy


def allowed(user):
    try:
        return queries_for(user)
    except QueryValidationError as e:
        raise PermissionDenied(str(e))


@login_required
@never_cache
def dashboard(request):
    queries = allowed(request.user)
    params = request.GET.copy()
    if not params:
        params.update({"period": "Hoy", "status": "Abierto"})
    form = Filters(params)
    if not form.is_valid():
        return render(
            request,
            "mahou/dashboard.html",
            {**context(request.user), "form": form, "invalid": True},
            status=400,
        )
    snap = Snapshot.objects.filter(pk=1).first()
    compatible = bool(
        snap and snap.updated_at and snap.signatures == signatures(queries)
    )
    rows = filtered(snap.rows, form.cleaned_data) if compatible else []
    if request.GET.get("format") == "csv":
        if not compatible:
            return HttpResponse(
                "No hay una actualización compatible disponible.", status=409
            )
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="mahou_panel.csv"'
        response.write("\ufeff")
        writer = csv.writer(response, delimiter=";")
        writer.writerow([v[1] for v in FIELDS])
        for row in rows:
            writer.writerow([csv_value(row.get(k)) for k, _, _ in FIELDS])
        return response
    cards, states = summary(rows)
    page = Paginator(rows, 100).get_page(request.GET.get("page"))
    link = params.copy()
    link.pop("page", None)
    link.pop("format", None)
    stale = bool(
        compatible
        and (
            (timezone.now() - snap.updated_at).total_seconds()
            > settings.MAHOU_REFRESH_SECONDS * 2
            or timezone.localdate(snap.updated_at) != timezone.localdate()
        )
    )
    return render(
        request,
        "mahou/dashboard.html",
        {
            **context(request.user),
            "form": form,
            "snapshot": snap,
            "compatible": compatible,
            "stale": stale,
            "cards": cards,
            "states": states,
            "page": page,
            "rows": present(page.object_list),
            "headers": [x[1] for x in FIELDS],
            "querystring": link.urlencode(),
            "docks": occupancy(snap.docks) if compatible else [],
            "load_docks": dock_groups(rows),
            "busy": bool(snap and snap.status in ("pending", "running")),
        },
    )


@login_required
@require_POST
def refresh(request):
    allowed(request.user)
    if request_refresh(request.user):
        messages.success(
            request, "Actualización solicitada. Se procesará en segundo plano."
        )
    else:
        messages.info(
            request,
            "Ya hay una actualización en curso o se ha solicitado hace menos de un minuto.",
        )
    return redirect("mahou_dashboard")
