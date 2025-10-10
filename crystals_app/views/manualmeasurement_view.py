from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import ManualMeasurement
import json


@require_http_methods(["GET"])
@jwt_required
@permission_required('read')
@log_api_access
def select_manual_measurements(request: HttpRequest):
    data = [model_to_dict(m) for m in ManualMeasurement.objects.all().order_by("id")]
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def add_manual_measurement(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    time = body.get("time")
    value = body.get("value")
    if time is None or value is None:
        return JsonResponse({"error": "time and value required"}, status=400)
    obj = ManualMeasurement.objects.create(time=time, value=value)
    return JsonResponse({"created": model_to_dict(obj)}, status=201)


@csrf_exempt
@require_http_methods(["POST"]) 
@jwt_required
@permission_required('read')
@log_api_access
def clear_manual_measurement_db(request: HttpRequest):
    ManualMeasurement.objects.all().delete()
    return JsonResponse({"cleared": True})
