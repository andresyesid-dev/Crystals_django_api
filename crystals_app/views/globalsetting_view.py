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
        gs = GlobalSetting.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).first()
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
        # Hay una sola fila de GlobalSetting por fábrica: filtrar por factory_id,
        # no por id global (mismo caso que Company). El id local del cliente es 1
        # porque su SQLite tiene una sola fábrica, pero en la nube multi-tenant
        # cada fábrica tiene su propio id (fábrica 3 -> id 2, etc.). Filtrar por
        # id=1 dejaba el update en 0 filas para las fábricas con id!=1 y, como
        # QuerySet.update() no lanza error, la API respondía "updated": True sin
        # haber guardado nada (las fábricas 3/4/5 no podían cambiar el color).
        GlobalSetting.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(line_color=color)
        return JsonResponse({"message": "✅ Color de línea actualizado", "updated": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar color", "error": str(e)}, status=500)
