from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import LaboratorySettingsExcel
import json


@require_http_methods(["GET"])
def get_laboratory_settings_excel_letters(request: HttpRequest):
    obj = LaboratorySettingsExcel.objects.filter(id=0).first()
    if not obj:
        return JsonResponse({"result": None})
    data = model_to_dict(obj)
    return JsonResponse({"result": {k: v for k, v in data.items() if k.endswith('_letter')}})


@require_http_methods(["GET"])
def get_laboratory_settings_excel_numbers(request: HttpRequest):
    obj = LaboratorySettingsExcel.objects.filter(id=0).first()
    if not obj:
        return JsonResponse({"result": None})
    data = model_to_dict(obj)
    return JsonResponse({"result": {k: v for k, v in data.items() if k.endswith('_number')}})


@csrf_exempt
@require_http_methods(["POST"])
def update_laboratory_settings_excel(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    obj, _ = LaboratorySettingsExcel.objects.get_or_create(id=0)
    for k, v in body.items():
        setattr(obj, k, v)
    obj.save()
    return JsonResponse({"updated": True})
