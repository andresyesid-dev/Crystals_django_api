from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import LaboratoryCalculatedMasaCParametrization
import json


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_laboratory_calculated_masa_c_parametrization(request: HttpRequest):
    try:
        data = []
        for o in LaboratoryCalculatedMasaCParametrization.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)):
            item = model_to_dict(o)
            if item.get("range_from") is not None:
                item["range_from"] = float(item["range_from"])
            if item.get("range_to") is not None:
                item["range_to"] = float(item["range_to"])
            data.append(item)
        return JsonResponse({"message": "✅ Datos obtenidos exitosamente", "results": data})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener parametrización Masa C calculada", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"]) 
@jwt_required
@sensitive_endpoint
@log_api_access
def update_laboratory_calculated_masa_c_parametrization(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        for parameter, categories in body.items():
            for categoria, ranges in (categories or {}).items():
                LaboratoryCalculatedMasaCParametrization.objects.filter(parameter=parameter, categoria=categoria, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(
                    range_from=ranges.get("range_from"), range_to=ranges.get("range_to")
                )
        return JsonResponse({"message": "✅ Parametrización Masa C calculada actualizada exitosamente", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar parametrización Masa C calculada", "error": str(e)}, status=500)
