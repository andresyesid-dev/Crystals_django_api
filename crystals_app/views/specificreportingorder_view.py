from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from django.db import models
from ..models import SpecificReportingOrder
import json


@require_http_methods(["GET"])
def get_specific_headers_ordering(request: HttpRequest):
    vals = list(SpecificReportingOrder.objects.order_by("ordering").values_list("value", flat=True))
    return JsonResponse({"results": vals})


@csrf_exempt
@require_http_methods(["POST"])
def update_specific_headers_order(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    value = body.get("value")
    ordering = body.get("ordering")
    if value is None or ordering is None:
        return JsonResponse({"error": "value and ordering required"}, status=400)
    SpecificReportingOrder.objects.filter(value=value).update(ordering=ordering)
    return JsonResponse({"ok": True})

@csrf_exempt
@require_http_methods(["POST"]) 
def insert_new_parameter_single_val(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    parameter_name = body.get("parameter_name")
    if not parameter_name:
        return JsonResponse({"error": "parameter_name required"}, status=400)
    max_order = SpecificReportingOrder.objects.aggregate(m=models.Max("ordering")).get("m") or 0
    SpecificReportingOrder.objects.create(value=str(parameter_name), ordering=max_order + 1)
    return JsonResponse({"ok": True})
