from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..models import Config
import json


def _get(key: str):
    """Helper function to get config value by key"""
    c = Config.objects.filter(key=key).first()
    return c.value if c else None


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_language(request: HttpRequest):
    try:
        return JsonResponse({"message": "✅ Idioma obtenido", "value": _get("language")})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener idioma", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_DOP_config(request: HttpRequest):
    try:
        v = _get("DOP graph divided")
        if v is None:
            return JsonResponse({"message": "❌ Configuración DOP no encontrada", "value": "error"})
        return JsonResponse({"message": "✅ Configuración DOP obtenida", "value": v == "on"})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener configuración DOP", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_calculated_data_period(request: HttpRequest):
    try:
        return JsonResponse({"message": "✅ Período obtenido", "value": _get("calculated data period")})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener período", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST", "PATCH"])
@jwt_required
@sensitive_endpoint
@log_api_access
def update_language(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        v = body.get("language")
        if not v:
            return JsonResponse({"message": "❌ El campo 'language' es requerido", "error": "language required"}, status=400)
        # Match local implementation: direct update
        Config.objects.filter(key="language").update(value=v)
        return JsonResponse({"message": "✅ Idioma actualizado", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar idioma", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST", "PATCH"])
@jwt_required
@sensitive_endpoint
@log_api_access
def update_DOP_config(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        checked = body.get("checked")
        val = "on" if checked else "off"
        # Match local implementation: direct update
        Config.objects.filter(key="DOP graph divided").update(value=val)
        return JsonResponse({"message": "✅ Configuración DOP actualizada", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar configuración DOP", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def update_calculated_data_period(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        period = body.get("period")
        if not period:
            return JsonResponse({"message": "❌ El campo 'period' es requerido", "error": "period required"}, status=400)
        # Match local implementation: direct update
        Config.objects.filter(key="calculated data period").update(value=period)
        return JsonResponse({"message": "✅ Período actualizado", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar período", "error": str(e)}, status=500)
        return JsonResponse({"message": "❌ Error al actualizar período", "error": str(e)}, status=500)
