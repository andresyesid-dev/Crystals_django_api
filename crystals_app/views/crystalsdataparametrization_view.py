from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import (
    CrystalsDataParametrization,
    CrystalsDataParametrizationMA,
    CrystalsDataParametrizationCV,
)
import json


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_crystals_data_parametrization(request: HttpRequest):
    try:
        data = [model_to_dict(o) for o in CrystalsDataParametrization.objects.all()]
        return JsonResponse({"message": "✅ Datos obtenidos exitosamente", "results": data})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener datos", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"]) 
@jwt_required
@sensitive_endpoint
@log_api_access
def update_crystals_data_parametrization(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        for parameter, categories in body.items():
            for categoria, ranges in (categories or {}).items():
                CrystalsDataParametrization.objects.filter(parameter=parameter, categoria=categoria).update(
                    range_from=ranges.get("range_from"), range_to=ranges.get("range_to")
                )
        return JsonResponse({"message": "✅ Actualizado exitosamente", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def exist_parameter_crystals_data_parametrization(request: HttpRequest):
    try:
        value = request.GET.get("value")
        belong = request.GET.get("belong")
        if value is None:
            return JsonResponse({"message": "❌ Falta el parámetro 'value'", "error": "value is required"}, status=400)
        exists = (
            CrystalsDataParametrization.objects.filter(parameter__icontains=value).exists()
            or (belong in (None, 'ma') and CrystalsDataParametrizationMA.objects.filter(parameter__icontains=value).exists())
            or (belong in (None, 'cv') and CrystalsDataParametrizationCV.objects.filter(parameter__icontains=value).exists())
        )
        return JsonResponse({"message": "✅ Consulta exitosa", "exists": exists})
    except Exception as e:
        return JsonResponse({"message": "❌ Error en la consulta", "error": str(e)}, status=500)
