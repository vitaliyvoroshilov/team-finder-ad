import json
from urllib.parse import urlencode

from django.core.paginator import Paginator

from team_finder.constants import PAGINATION_PER_PAGE


def build_page_context(request, queryset, *, base_context=None):
    paginator = Paginator(queryset, PAGINATION_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    query_prefix = f"{urlencode(params)}&" if params else ""
    context = {"page_obj": page_obj, "query_prefix": query_prefix}
    if base_context:
        context.update(base_context)
    return context


def load_json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return {}
