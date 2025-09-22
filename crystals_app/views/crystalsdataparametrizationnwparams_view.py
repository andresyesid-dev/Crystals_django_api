from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import CrystalsDataParametrizationNewParams
import json


@require_http_methods(["GET"])
def get_crystals_data_parametrization_nw_params(request: HttpRequest):
    data = [model_to_dict(o) for o in CrystalsDataParametrizationNewParams.objects.all()]
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"]) 
def update_crystals_data_parametrization_nw_params(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    for parameter, categories in body.items():
        for categoria, ranges in (categories or {}).items():
            CrystalsDataParametrizationNewParams.objects.filter(parameter=parameter, categoria=categoria).update(
                range_from=ranges.get("range_from"), range_to=ranges.get("range_to")
            )
    return JsonResponse({"ok": True})


@csrf_exempt
@require_http_methods(["POST"]) 
def add_new_newprms_parameters(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    params = body.get("parameters") or []
    existing = set(CrystalsDataParametrizationNewParams.objects.values_list("parameter", flat=True))
    incoming = set(params)
    to_add = incoming - existing
    for parametro in to_add:
        for categoria in ["Good", "Regular", "Bad"]:
            CrystalsDataParametrizationNewParams.objects.create(parameter=parametro, categoria=categoria)
    CrystalsDataParametrizationNewParams.objects.exclude(parameter__in=incoming).delete()
    return JsonResponse({"ok": True, "added": list(to_add)})
