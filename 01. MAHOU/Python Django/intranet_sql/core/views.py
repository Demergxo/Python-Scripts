from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Q


from .forms import QuerySelectForm, build_query_run_form
from .models import Query, QueryCategory, UserCategoryAccess
from .services import execute_query, QueryValidationError, get_visible_categories_for_user

import csv
from io import BytesIO, StringIO
from openpyxl import Workbook

from urllib.parse import urlencode

@login_required
def home(request):
    user = request.user
    user_groups = user.groups.all()

    is_admin = (user.is_staff or user.groups.filter(name="Admin").exists())

    # Categorías visibles por grupo:
    # - Si allowed_groups está vacío => visible para todos
    # - O si intersecta con los grupos del usuario
    group_visible = QueryCategory.objects.filter(
        Q(allowed_groups__isnull=True) | Q(allowed_groups__in=user_groups)
    ).distinct()

    # Categorías extra por usuario
    extra = QueryCategory.objects.none()
    access = UserCategoryAccess.objects.filter(user=user).first()
    if access:
        extra = access.extra_categories.all()

    visible_categories = (group_visible | extra).distinct().order_by("order", "name")

    # Queries solo de categorías visibles (y activas)
    queries = (
        Query.objects.filter(is_active=True, category__in=visible_categories)
        .select_related("category")
        .order_by("name")
    )

    grouped = {c: [] for c in visible_categories}
    for q in queries:
        grouped[q.category].append(q) #type:ignore

    return render(request, "workspace.html", {
        "categories": list(visible_categories),
        "grouped": grouped,
        "uncategorized": [],  # opcional: si quieres restringir también las sin categoría
        "is_admin": is_admin,
        "sidebar_mode": "workspace",
    })


@login_required
def run_query(request, code: str):
    print(">>> ESTOY EN run_query, METHOD:", request.method)
    q = get_object_or_404(Query, code=code, is_active=True)

    user = request.user
    user_groups = user.groups.all()

    group_visible = QueryCategory.objects.filter(
        Q(allowed_groups__isnull=True) | Q(allowed_groups__in=user_groups)
    ).distinct()

    extra = QueryCategory.objects.none()
    access = UserCategoryAccess.objects.filter(user=user).first()
    if access:
        extra = access.extra_categories.all()

    visible = (group_visible | extra).distinct().order_by("order", "name")
    visible_categories = list(visible)

    is_admin = (user.is_staff or user.groups.filter(name="Admin").exists())

    # si no tiene categoria, se prohibe

    if q.category is None:
        return HttpResponseForbidden("Acceso denegado a esta consulta.")

    if not visible.filter(pk=q.category_id).exists(): #type:ignore
        return HttpResponseForbidden("Acceso denegado a esta consulta.")

    FormClass = build_query_run_form(q)

    if request.method == "POST":
        form = FormClass(request.POST)
        if form.is_valid(): #type:ignore
            try:
                cols, rows = execute_query(q.code, request.user, form.cleaned_data) #type:ignore
            except QueryValidationError as e:
                form.add_error(None, str(e)) #type:ignore
                return render(request, "query_run.html", {"query": q, "form": form, "ran": False}) #type:ignore

            # Convertimos a string para meterlo en la URL
            export_param = {k: (v.isoformat() if hasattr(v, 'isoformat') else str(v)) for k,v in form.cleaned_data.items() if v is not None}
            export_qs = urlencode(export_param)

            return render(request, "query_run.html", {
                "query": q,
                "form": form,
                "cols": cols,
                "rows": rows,
                "ran": True,
                "export_qs": export_qs,
                "categories": visible_categories,
                "is_admin": is_admin,
                "sidebar_mode": "links",
            })
    else:
        form = FormClass()

    return render(request, "query_run.html", {"query": q, "form": form, "ran": False, "categories": visible_categories, "is_admin": is_admin, "sidebar_mode": "links",})

@login_required
def export_csv(request, code: str):
    q = get_object_or_404(Query, code=code, is_active=True)

    params = request.POST if request.method == "POST" else request.GET
    cols, rows = execute_query(q.code, request.user, params)

    # Create a BytesIO buffer

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    ts = timezone.localtime().strftime("%Y%m%d_%H%M%S")
    response["Content-Disposition"] = f'attachment; filename="{q.code}_{ts}.csv"'

    writer = csv.writer(response)
    writer.writerow(cols)
    for row in rows:
        writer.writerow(row)

    return response

@login_required
def export_excel(request, code: str):
    q = get_object_or_404(Query, code=code, is_active=True)

    params = request.POST if request.method == "POST" else request.GET
    cols, rows = execute_query(q.code, request.user, params)


    # Create a BytesIO buffer
    buffer = BytesIO()

    # Create a workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = q.code #type:ignore

    # Write headers
    ws.append(cols) #type:ignore

    # Write data rows
    for row in rows:
        ws.append(list(row))#type:ignore

    # Save the workbook to the buffer
    wb.save(buffer)

    # Prepare the response
    buffer.seek(0)
    ts = timezone.localtime().strftime("%Y%m%d_%H%M%S")
    response = HttpResponse(
        buffer, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{q.code}_{ts}.xlsx"'

    return response


@login_required
def query_detail(request, code: str):
    user = request.user

    # Categorías visibles (mismo cálculo que en run_query)
    user_groups = user.groups.all()
    group_visible = QueryCategory.objects.filter(
        Q(allowed_groups__isnull=True) | Q(allowed_groups__in=user_groups)
    ).distinct()

    extra = QueryCategory.objects.none()
    access = UserCategoryAccess.objects.filter(user=user).first()
    if access:
        extra = access.extra_categories.all()

    visible = (group_visible | extra).distinct().order_by("order", "name")
    visible_categories = list(visible)

    is_admin = (user.is_staff or user.groups.filter(name="Admin").exists())

    q = get_object_or_404(Query, code=code, is_active=True)

    # (Opcional pero recomendable) evitar que alguien entre a una query que no puede ver
    if q.category and not visible.filter(pk=q.category.pk).exists():
        # aquí puedes devolver 403 si ya lo estás haciendo en run_query
        
        return HttpResponseForbidden("No tienes permisos para ver esta consulta.")

    FormClass = build_query_run_form(q)
    form = FormClass()  # vacío (GET)

    return render(request, "query_detail.html", {
        "query": q,
        "form": form,
        "categories": visible_categories,
        "is_admin": is_admin,
        "sidebar_mode": "links",
    })


