from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import CrudoCalculation
import json


@require_http_methods(["GET"])
def get_crudo_calculations(request: HttpRequest):
    data = [model_to_dict(o) for o in CrudoCalculation.objects.all()]
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"])
def insert_crudo_calculations(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    payload = body.get("data") or []
    created = 0
    for item in payload:
        fields = {
            "ti": item.get("ti"),
            "ft3_per_templa": item.get("ft3_per_templa"),
            "bx_masa_c": item.get("bx_masa_c") or item.get("bx_masa__c"),
            "no_templas": item.get("no_templas"),
            "porcentaje_cristales": item.get("porcentaje_cristales"),
            "tamano_final_polv": item.get("tamano_final_polv"),
            "concentracion_slurry": item.get("concentracion_slurry"),
            "alcohol_slurry": item.get("alcohol_slurry"),
            "densidad_slurry": item.get("densidad_slurry"),
        }
        CrudoCalculation.objects.create(**fields)
        created += 1
    return JsonResponse({"ok": True, "created": created})
