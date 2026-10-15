from core.models import Query
from core.services import get_visible_categories_for_user


def navigation(request):
    user = request.user
    visible = False
    if user.is_authenticated and user.is_active:
        qs = Query.objects.filter(
            code__in=["MAHOU_PANEL", "MAHOU_MUELLES"], is_active=True
        )
        if not user.is_superuser:
            qs = qs.filter(category__in=get_visible_categories_for_user(user))
        visible = qs.count() == 2
    return {"can_view_mahou": visible}
