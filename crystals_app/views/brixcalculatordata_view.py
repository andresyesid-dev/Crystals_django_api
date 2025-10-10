from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import BrixCalculatorData
import json


@require_http_methods(["GET"])
@jwt_required
@permission_required('read')
@log_api_access
def get_brix_calculator_data(request: HttpRequest):
    data = [model_to_dict(o) for o in BrixCalculatorData.objects.all().order_by("tc")]
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def update_brix_calculator_data(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    tc = body.get("tc")
    pureza = body.get("pureza")
    ss = body.get("ss")
    brx = body.get("brx")
    if tc is None:
        return JsonResponse({"error": "tc required"}, status=400)
    obj, _ = BrixCalculatorData.objects.get_or_create(tc=tc)
    if pureza is not None:
        obj.pureza = pureza
    if ss is not None:
        obj.ss = ss
    if brx is not None:
        obj.brx = brx
    obj.save()
    return JsonResponse({"updated": model_to_dict(obj)})
