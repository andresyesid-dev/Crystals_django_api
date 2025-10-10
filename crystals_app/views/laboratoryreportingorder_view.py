from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..models import LaboratoryReportingOrder
import json


@require_http_methods(["GET"])
@jwt_required
@permission_required('read')
@log_api_access
def get_laboratory_headers_ordering(request: HttpRequest):
    vals = list(LaboratoryReportingOrder.objects.order_by("ordering").values_list("value", flat=True))
    return JsonResponse({"results": vals})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def update_laboratory_headers_order(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    value = body.get("value")
    ordering = body.get("ordering")
    if value is None or ordering is None:
        return JsonResponse({"error": "value and ordering required"}, status=400)
    LaboratoryReportingOrder.objects.filter(value=value).update(ordering=ordering)
    return JsonResponse({"ok": True})
