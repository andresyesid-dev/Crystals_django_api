from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from django.db import models
from ..models import SpecificReportingOrder
import json


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_specific_headers_ordering(request: HttpRequest):
    try:
        vals = list(SpecificReportingOrder.objects.order_by("ordering").values_list("value", flat=True))
        return JsonResponse({"message": "✅ Orden de encabezados específicos obtenido exitosamente", "results": vals})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener orden de encabezados específicos", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def update_specific_headers_order(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        value = body.get("value")
        ordering = body.get("ordering")
        if value is None or ordering is None:
            return JsonResponse({"message": "❌ Los campos 'value' y 'ordering' son requeridos", "error": "value and ordering required"}, status=400)
        SpecificReportingOrder.objects.filter(value=value).update(ordering=ordering)
        return JsonResponse({"message": "✅ Orden de encabezados actualizado exitosamente", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar orden de encabezados", "error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"]) 
@jwt_required
@sensitive_endpoint
@log_api_access
def insert_new_parameter_single_val(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        parameter_name = body.get("parameter_name")
        if not parameter_name:
            return JsonResponse({"message": "❌ El campo 'parameter_name' es requerido", "error": "parameter_name required"}, status=400)
        max_order = SpecificReportingOrder.objects.aggregate(m=models.Max("ordering")).get("m") or 0
        SpecificReportingOrder.objects.create(value=str(parameter_name), ordering=max_order + 1)
        return JsonResponse({"message": "✅ Nuevo parámetro insertado exitosamente", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al insertar nuevo parámetro", "error": str(e)}, status=500)
