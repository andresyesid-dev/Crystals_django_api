from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import GlobalSetting
import json


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_line_color(request: HttpRequest):
    try:
        # Match local implementation: get first record (no WHERE clause in local)
        gs = GlobalSetting.objects.first()
        return JsonResponse({"message": "✅ Color de línea obtenido", "line_color": gs.line_color if gs else None})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener color de línea", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def update_line_color(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        color = body.get("line_color")
        if not color:
            return JsonResponse({"message": "❌ El campo 'line_color' es requerido", "error": "line_color required"}, status=400)
        # Match local implementation: direct update on id=1
        GlobalSetting.objects.filter(id=1).update(line_color=color)
        return JsonResponse({"message": "✅ Color de línea actualizado", "updated": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar color", "error": str(e)}, status=500)
