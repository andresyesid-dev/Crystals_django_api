from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import (
    LaboratoryParametrization,
    LaboratoryCalculatedRefinoParametrization,
    LaboratoryCalculatedMasaAParametrization,
    LaboratoryCalculatedMasaBParametrization,
    LaboratoryCalculatedMasaCParametrization,
)
import json


@require_http_methods(["GET"])
def get_laboratory_parametrization(request: HttpRequest):
    data = [model_to_dict(o) for o in LaboratoryParametrization.objects.all()]
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"])
def update_laboratory_parametrization(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    for material, categories in body.items():
        for categoria, ranges in (categories or {}).items():
            LaboratoryParametrization.objects.filter(material=material, categoria=categoria).update(
                range_from=ranges.get("range_from"), range_to=ranges.get("range_to")
            )
    return JsonResponse({"ok": True})


@require_http_methods(["GET"])
def get_laboratory_calculated_refino_parametrization(request: HttpRequest):
    data = [model_to_dict(o) for o in LaboratoryCalculatedRefinoParametrization.objects.all()]
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"])
def update_laboratory_calculated_refino_parametrization(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    for parameter, categories in body.items():
        for categoria, ranges in (categories or {}).items():
            LaboratoryCalculatedRefinoParametrization.objects.filter(parameter=parameter, categoria=categoria).update(
                range_from=ranges.get("range_from"), range_to=ranges.get("range_to")
            )
    return JsonResponse({"ok": True})


@require_http_methods(["GET"])
def get_laboratory_calculated_masa_a_parametrization(request: HttpRequest):
    data = [model_to_dict(o) for o in LaboratoryCalculatedMasaAParametrization.objects.all()]
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"])
def update_laboratory_calculated_masa_a_parametrization(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    for parameter, categories in body.items():
        for categoria, ranges in (categories or {}).items():
            LaboratoryCalculatedMasaAParametrization.objects.filter(parameter=parameter, categoria=categoria).update(
                range_from=ranges.get("range_from"), range_to=ranges.get("range_to")
            )
    return JsonResponse({"ok": True})


@require_http_methods(["GET"])
def get_laboratory_calculated_masa_b_parametrization(request: HttpRequest):
    data = [model_to_dict(o) for o in LaboratoryCalculatedMasaBParametrization.objects.all()]
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"])
def update_laboratory_calculated_masa_b_parametrization(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    for parameter, categories in body.items():
        for categoria, ranges in (categories or {}).items():
            LaboratoryCalculatedMasaBParametrization.objects.filter(parameter=parameter, categoria=categoria).update(
                range_from=ranges.get("range_from"), range_to=ranges.get("range_to")
            )
    return JsonResponse({"ok": True})


@require_http_methods(["GET"])
def get_laboratory_calculated_masa_c_parametrization(request: HttpRequest):
    data = [model_to_dict(o) for o in LaboratoryCalculatedMasaCParametrization.objects.all()]
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"])
def update_laboratory_calculated_masa_c_parametrization(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    for parameter, categories in body.items():
        for categoria, ranges in (categories or {}).items():
            LaboratoryCalculatedMasaCParametrization.objects.filter(parameter=parameter, categoria=categoria).update(
                range_from=ranges.get("range_from"), range_to=ranges.get("range_to")
            )
    return JsonResponse({"ok": True})
