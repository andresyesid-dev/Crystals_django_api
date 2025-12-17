from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from django.db.models import Q
from ..models import (
    CrystalsDataParametrization,
    CrystalsDataParametrizationMA,
    CrystalsDataParametrizationCV,
    CrystalsDataParametrizationNewParams,
)
import json


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_crystals_data_parametrization(request: HttpRequest):
    try:
        data = []
        for o in CrystalsDataParametrization.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)):
            item = model_to_dict(o)
            # Ensure ranges are floats, not Decimals/strings
            if item.get("range_from") is not None:
                item["range_from"] = float(item["range_from"])
            if item.get("range_to") is not None:
                item["range_to"] = float(item["range_to"])
            data.append(item)
        return JsonResponse({"message": "✅ Parametrización de datos de cristales obtenida exitosamente", "results": data})
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
                CrystalsDataParametrization.objects.filter(parameter=parameter, categoria=categoria, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(
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
            
        # Normalize search terms
        val_lower = value.lower()
        val_space = val_lower.replace('_', ' ')
        val_underscore = val_lower.replace(' ', '_')
        
        factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
        
        # Check logic with normalized values across all tables
        exists = False
        
        # 1. Check Default tables (if no specific belong or belong matches default context implicitly)
        # Note: 'belong' is usually [ma] or [cv]. If None, check everything.
        if not belong:
            exists = CrystalsDataParametrization.objects.filter(
                Q(parameter__iexact=val_space) | Q(parameter__iexact=val_underscore),
                factory_id=factory_id
            ).exists()
            
            if not exists:
                exists = CrystalsDataParametrizationNewParams.objects.filter(
                    Q(parameter__iexact=val_space) | Q(parameter__iexact=val_underscore),
                    factory_id=factory_id
                ).exists()

        # 2. Check MA
        if not exists and (not belong or belong == '[ma]'):
            exists = CrystalsDataParametrizationMA.objects.filter(
                Q(parameter__iexact=val_space) | Q(parameter__iexact=val_underscore),
                factory_id=factory_id
            ).exists()

        # 3. Check CV
        if not exists and (not belong or belong == '[cv]'):
            exists = CrystalsDataParametrizationCV.objects.filter(
                Q(parameter__iexact=val_space) | Q(parameter__iexact=val_underscore),
                factory_id=factory_id
            ).exists()

        return JsonResponse({"message": "✅ Consulta exitosa", "exists": exists})
    except Exception as e:
        return JsonResponse({"message": "❌ Error en la consulta", "error": str(e)}, status=500)
