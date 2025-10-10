from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import RefinoCalculation
import json


@require_http_methods(["GET"])
@jwt_required
@permission_required('read')
@log_api_access
def get_refino_calculations(request: HttpRequest):
    data = [model_to_dict(o) for o in RefinoCalculation.objects.all()]
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def insert_refino_calculations(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    payload = body.get("data") or []
    created = 0
    for item in payload:
        fields = {
            "am_azucar": item.get("am_azucar"),
            "temperatura": item.get("temperatura"),
            "volumen_tacho": item.get("volumen_tacho"),
            "densidad_grano": item.get("densidad_grano"),
            "rendimiento_solidos": item.get("rendimiento_solidos"),
            "concentracion_masacocida": item.get("concentracion_masacocida"),
            "am_semilla_lock": item.get("am_semilla_lock"),
            "concentracion_slurry": item.get("concentracion_slurry"),
            "alcohol_slurry": item.get("alcohol_slurry"),
            "densidad_slurry": item.get("densidad_slurry"),
        }
        RefinoCalculation.objects.create(**fields)
        created += 1
    return JsonResponse({"ok": True, "created": created})
