from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..models import Config
import json


@jwt_required
@permission_required('read')
@log_api_access
def _get(key: str):
    c = Config.objects.filter(key=key).first()
    return c.value if c else None


@require_http_methods(["GET"])
@jwt_required
@permission_required('read')
@log_api_access
def get_language(request: HttpRequest):
    return JsonResponse({"value": _get("language")})


@require_http_methods(["GET"])
@jwt_required
@permission_required('read')
@log_api_access
def get_DOP_config(request: HttpRequest):
    v = _get("DOP graph divided")
    if v is None:
        return JsonResponse({"value": "error"})
    return JsonResponse({"value": v == "on"})


@require_http_methods(["GET"])
@jwt_required
@permission_required('read')
@log_api_access
def get_calculated_data_period(request: HttpRequest):
    return JsonResponse({"value": _get("calculated data period")})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def update_language(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    v = body.get("language")
    if not v:
        return JsonResponse({"error": "language required"}, status=400)
    Config.objects.update_or_create(key="language", defaults={"value": v})
    return JsonResponse({"ok": True})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('admin')
@sensitive_endpoint
@log_api_access
def update_DOP_config(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    checked = body.get("checked")
    val = "on" if checked else "off"
    Config.objects.update_or_create(key="DOP graph divided", defaults={"value": val})
    return JsonResponse({"ok": True})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def update_calculated_data_period(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    period = body.get("period")
    if not period:
        return JsonResponse({"error": "period required"}, status=400)
    Config.objects.update_or_create(key="calculated data period", defaults={"value": period})
    return JsonResponse({"ok": True})
