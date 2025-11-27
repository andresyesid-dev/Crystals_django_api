from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import CrystalsDataParametrizationMA
import json


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_crystals_data_parametrization_ma(request: HttpRequest):
    try:
        data = [model_to_dict(o) for o in CrystalsDataParametrizationMA.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1))]
        return JsonResponse({"message": "✅ Parametrización MA obtenida", "results": data})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener parametrización MA", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"]) 
@jwt_required
@sensitive_endpoint
@log_api_access
def update_crystals_data_parametrization_ma(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        for parameter, categories in body.items():
            for categoria, ranges in (categories or {}).items():
                if categoria == 'Good' and 'tolerance' in ranges:
                    CrystalsDataParametrizationMA.objects.filter(parameter=parameter, categoria='Good', factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(
                        tolerance=ranges.get("tolerance")
                    )
                CrystalsDataParametrizationMA.objects.filter(parameter=parameter, categoria=categoria, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(
                    range_from=ranges.get("range_from"), range_to=ranges.get("range_to")
                )
        return JsonResponse({"message": "✅ Parametrización MA actualizada", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar parametrización MA", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"]) 
@jwt_required
@sensitive_endpoint
@log_api_access
def update_specific_parametrization_ma(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        calibration = body.get("calibration")
        specific_parameter = body.get("specific_parameter") or []
        tolerance = body.get("tolerance")
        if not calibration or len(specific_parameter) != 3:
            return JsonResponse({"message": "❌ Se requiere calibration y 3 rangos de categorías", "error": "calibration and 3-category ranges required"}, status=400)
        for categoria, ranges in zip(["Good", "Regular", "Bad"], specific_parameter):
            if categoria == "Good" and tolerance is not None:
                CrystalsDataParametrizationMA.objects.filter(parameter=calibration, categoria="Good", factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(
                    tolerance=tolerance
                )
            CrystalsDataParametrizationMA.objects.filter(parameter=calibration, categoria=categoria, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(
                range_from=ranges[0], range_to=ranges[1]
            )
        return JsonResponse({"message": "✅ Parametrización específica MA actualizada", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar parametrización específica MA", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"]) 
@jwt_required
@sensitive_endpoint
@log_api_access
def add_new_ma_parameters(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        params = body.get("parameters") or []
        existing = set(CrystalsDataParametrizationMA.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).values_list("parameter", flat=True))
        incoming = set(params)
        to_add = incoming - existing
        for parametro in to_add:
            for categoria in ["Good", "Regular", "Bad"]:
                CrystalsDataParametrizationMA.objects.create(parameter=parametro, categoria=categoria, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1))
        CrystalsDataParametrizationMA.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).exclude(parameter__in=incoming).delete()
        return JsonResponse({"message": "✅ Parámetros MA agregados exitosamente", "ok": True, "added": list(to_add)})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al agregar parámetros MA", "error": str(e)}, status=500)
