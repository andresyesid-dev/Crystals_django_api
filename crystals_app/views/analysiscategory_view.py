from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..models import AnalysisCategory, NewParametersAnalysisCategory, SpecificReportingOrder
import json


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def add_analysis_cat_values(request: HttpRequest):
    # payload: {"historic_reports_id": id, "values": [[param, value], ...]}
    body = json.loads(request.body or b"{}")
    hr_id = body.get("historic_reports_id")
    values = body.get("values") or []
    if not hr_id:
        return JsonResponse({"error": "historic_reports_id required"}, status=400)
    data = {k: (v if v != "" else None) for k, v in values}
    data["historic_report_id"] = hr_id
    AnalysisCategory.objects.create(**data)
    return JsonResponse({"ok": True})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def add_new_parameters_analysis_categories(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    parameter = (body.get("parameter") or "").replace(' ', '_')
    type_ = body.get("type")
    if not parameter or not type_:
        return JsonResponse({"error": "parameter and type required"}, status=400)
    NewParametersAnalysisCategory.objects.create(parameter=parameter, type=type_)
    return JsonResponse({"ok": True})


@require_http_methods(["GET"])
@jwt_required
@permission_required('read')
@log_api_access
def get_new_parameters_analysis_categories(request: HttpRequest):
    data = list(NewParametersAnalysisCategory.objects.all().values())
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def delete_parameter_analysis_category(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    parameter = (body.get("parameter") or "").replace(' ', '_')
    if not parameter:
        return JsonResponse({"error": "parameter required"}, status=400)
    NewParametersAnalysisCategory.objects.filter(parameter=parameter).delete()
    SpecificReportingOrder.objects.filter(value=parameter.replace('_', ' ')).delete()
    return JsonResponse({"deleted": True})
