from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import CrystalsDataParametrizationNewParams
import json


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_crystals_data_parametrization_nw_params(request: HttpRequest):
    try:
        data = [model_to_dict(o) for o in CrystalsDataParametrizationNewParams.objects.all()]
        return JsonResponse({"message": "✅ Parametrización nuevos parámetros obtenida", "results": data})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener parametrización", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"]) 
@jwt_required
@sensitive_endpoint
@log_api_access
def update_crystals_data_parametrization_nw_params(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        for parameter, categories in body.items():
            for categoria, ranges in (categories or {}).items():
                CrystalsDataParametrizationNewParams.objects.filter(parameter=parameter, categoria=categoria).update(
                    range_from=ranges.get("range_from"), range_to=ranges.get("range_to")
                )
        return JsonResponse({"message": "✅ Parametrización actualizada exitosamente", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar parametrización", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"]) 
@jwt_required
@sensitive_endpoint
@log_api_access
def add_new_newprms_parameters(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        params = body.get("parameters") or []
        existing = set(CrystalsDataParametrizationNewParams.objects.values_list("parameter", flat=True))
        incoming = set(params)
        to_add = incoming - existing
        for parametro in to_add:
            for categoria in ["Good", "Regular", "Bad"]:
                CrystalsDataParametrizationNewParams.objects.create(parameter=parametro, categoria=categoria)
        CrystalsDataParametrizationNewParams.objects.exclude(parameter__in=incoming).delete()
        return JsonResponse({"message": "✅ Parámetros agregados exitosamente", "ok": True, "added": list(to_add)})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al agregar parámetros", "error": str(e)}, status=500)
