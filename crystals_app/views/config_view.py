from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..models import Config
import json


def _get(key: str):
    c = Config.objects.filter(key=key).first()
    return c.value if c else None


@require_http_methods(["GET"])
def get_language(request: HttpRequest):
    return JsonResponse({"value": _get("language")})


@require_http_methods(["GET"])
def get_DOP_config(request: HttpRequest):
    v = _get("DOP graph divided")
    if v is None:
        return JsonResponse({"value": "error"})
    return JsonResponse({"value": v == "on"})


@require_http_methods(["GET"])
def get_calculated_data_period(request: HttpRequest):
    return JsonResponse({"value": _get("calculated data period")})


@csrf_exempt
@require_http_methods(["POST"])
def update_language(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    v = body.get("language")
    if not v:
        return JsonResponse({"error": "language required"}, status=400)
    Config.objects.update_or_create(key="language", defaults={"value": v})
    return JsonResponse({"ok": True})


@csrf_exempt
@require_http_methods(["POST"])
def update_DOP_config(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    checked = body.get("checked")
    val = "on" if checked else "off"
    Config.objects.update_or_create(key="DOP graph divided", defaults={"value": val})
    return JsonResponse({"ok": True})


@csrf_exempt
@require_http_methods(["POST"])
def update_calculated_data_period(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    period = body.get("period")
    if not period:
        return JsonResponse({"error": "period required"}, status=400)
    Config.objects.update_or_create(key="calculated data period", defaults={"value": period})
    return JsonResponse({"ok": True})
