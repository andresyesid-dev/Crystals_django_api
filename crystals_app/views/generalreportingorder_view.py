from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..models import GeneralReportingOrder
import json


@require_http_methods(["GET"])
def get_general_headers_ordering(request: HttpRequest):
    vals = list(GeneralReportingOrder.objects.order_by("ordering").values_list("value", flat=True))
    return JsonResponse({"results": vals})


@csrf_exempt
@require_http_methods(["POST"])
def update_general_headers_order(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    value = body.get("value")
    ordering = body.get("ordering")
    if value is None or ordering is None:
        return JsonResponse({"error": "value and ordering required"}, status=400)
    GeneralReportingOrder.objects.filter(value=value).update(ordering=ordering)
    return JsonResponse({"ok": True})
