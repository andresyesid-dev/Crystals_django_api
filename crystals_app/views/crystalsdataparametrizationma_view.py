from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import CrystalsDataParametrizationMA
import json


@require_http_methods(["GET"])
def get_crystals_data_parametrization_ma(request: HttpRequest):
    data = [model_to_dict(o) for o in CrystalsDataParametrizationMA.objects.all()]
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"]) 
def update_crystals_data_parametrization_ma(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    for parameter, categories in body.items():
        for categoria, ranges in (categories or {}).items():
            if categoria == 'Good' and 'tolerance' in ranges:
                CrystalsDataParametrizationMA.objects.filter(parameter=parameter, categoria='Good').update(
                    tolerance=ranges.get("tolerance")
                )
            CrystalsDataParametrizationMA.objects.filter(parameter=parameter, categoria=categoria).update(
                range_from=ranges.get("range_from"), range_to=ranges.get("range_to")
            )
    return JsonResponse({"ok": True})


@csrf_exempt
@require_http_methods(["POST"]) 
def update_specific_parametrization_ma(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    calibration = body.get("calibration")
    specific_parameter = body.get("specific_parameter") or []
    tolerance = body.get("tolerance")
    if not calibration or len(specific_parameter) != 3:
        return JsonResponse({"error": "calibration and 3-category ranges required"}, status=400)
    for categoria, ranges in zip(["Good", "Regular", "Bad"], specific_parameter):
        if categoria == "Good" and tolerance is not None:
            CrystalsDataParametrizationMA.objects.filter(parameter=calibration, categoria="Good").update(
                tolerance=tolerance
            )
        CrystalsDataParametrizationMA.objects.filter(parameter=calibration, categoria=categoria).update(
            range_from=ranges[0], range_to=ranges[1]
        )
    return JsonResponse({"ok": True})


@csrf_exempt
@require_http_methods(["POST"]) 
def add_new_ma_parameters(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    params = body.get("parameters") or []
    existing = set(CrystalsDataParametrizationMA.objects.values_list("parameter", flat=True))
    incoming = set(params)
    to_add = incoming - existing
    for parametro in to_add:
        for categoria in ["Good", "Regular", "Bad"]:
            CrystalsDataParametrizationMA.objects.create(parameter=parametro, categoria=categoria)
    CrystalsDataParametrizationMA.objects.exclude(parameter__in=incoming).delete()
    return JsonResponse({"ok": True, "added": list(to_add)})
