from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import ManagementReportSettings
import json


@require_http_methods(["GET"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def get_management_report_settings(request: HttpRequest):
    obj = ManagementReportSettings.objects.first()
    return JsonResponse({"result": model_to_dict(obj) if obj else None})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def insert_management_report_settings(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    obj = ManagementReportSettings.objects.create(**body)
    return JsonResponse({"created": model_to_dict(obj)})


@csrf_exempt
@require_http_methods(["POST", "PATCH"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def update_management_report_settings(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    m_r_id = body.get("id")
    if not m_r_id:
        return JsonResponse({"error": "id required"}, status=400)
    try:
        obj = ManagementReportSettings.objects.get(id=m_r_id)
    except ManagementReportSettings.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)
    for k, v in body.items():
        if k != "id":
            setattr(obj, k, v)
    obj.save()
    return JsonResponse({"updated": model_to_dict(obj)})
