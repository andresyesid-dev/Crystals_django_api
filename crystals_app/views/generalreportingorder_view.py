from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..models import GeneralReportingOrder
import json


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_general_headers_ordering(request: HttpRequest):
    try:
        vals = list(GeneralReportingOrder.objects.order_by("ordering").values_list("value", flat=True))
        return JsonResponse({"message": "✅ Orden de encabezados obtenido", "results": vals})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener orden", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def update_general_headers_order(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        value = body.get("value")
        ordering = body.get("ordering")
        if value is None or ordering is None:
            return JsonResponse({"message": "❌ Los campos 'value' y 'ordering' son requeridos", "error": "value and ordering required"}, status=400)
        GeneralReportingOrder.objects.filter(value=value).update(ordering=ordering)
        return JsonResponse({"message": "✅ Orden actualizado exitosamente", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar orden", "error": str(e)}, status=500)
