from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..models import NewParametersAnalysisCategory
import json


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def add_new_parameter(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        parameter = (body.get("parameter") or "").replace(' ', '_')
        type_ = body.get("type")
        if not parameter or not type_:
            return JsonResponse({"message": "❌ Los campos 'parameter' y 'type' son requeridos", "error": "parameter and type required"}, status=400)
        NewParametersAnalysisCategory.objects.create(parameter=parameter, type=type_, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1))
        return JsonResponse({"message": "✅ Nuevo parámetro agregado exitosamente", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al agregar nuevo parámetro", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_new_parameters(request: HttpRequest):
    try:
        data = list(NewParametersAnalysisCategory.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).values())
        return JsonResponse({"message": "✅ Nuevos parámetros obtenidos exitosamente", "results": data})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener nuevos parámetros", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def delete_new_parameter(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        parameter = (body.get("parameter") or "").replace(' ', '_')
        if not parameter:
            return JsonResponse({"message": "❌ El campo 'parameter' es requerido", "error": "parameter required"}, status=400)
        NewParametersAnalysisCategory.objects.filter(parameter=parameter, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).delete()
        return JsonResponse({"message": "✅ Nuevo parámetro eliminado exitosamente", "deleted": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al eliminar nuevo parámetro", "error": str(e)}, status=500)
