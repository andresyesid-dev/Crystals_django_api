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
@permission_required('read')
@log_api_access
def get_crystals_data_parametrization(request: HttpRequest):
    data = [model_to_dict(o) for o in CrystalsDataParametrization.objects.all()]
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"]) 
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def update_crystals_data_parametrization(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    for parameter, categories in body.items():
        for categoria, ranges in (categories or {}).items():
            CrystalsDataParametrization.objects.filter(parameter=parameter, categoria=categoria).update(
                range_from=ranges.get("range_from"), range_to=ranges.get("range_to")
            )
    return JsonResponse({"ok": True})


@require_http_methods(["GET"])
@jwt_required
@permission_required('read')
@log_api_access
def exist_parameter_crystals_data_parametrization(request: HttpRequest):
    value = request.GET.get("value")
    belong = request.GET.get("belong")
    if value is None:
        return JsonResponse({"exists": False})
    exists = (
        CrystalsDataParametrization.objects.filter(parameter__icontains=value).exists()
        or (belong in (None, 'ma') and CrystalsDataParametrizationMA.objects.filter(parameter__icontains=value).exists())
        or (belong in (None, 'cv') and CrystalsDataParametrizationCV.objects.filter(parameter__icontains=value).exists())
    )
    return JsonResponse({"exists": exists})
