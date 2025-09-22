from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import LaboratoryData
import json


@require_http_methods(["GET"])
def get_laboratory_data(request: HttpRequest):
    obj = LaboratoryData.objects.filter(id=0).first()
    return JsonResponse({"result": model_to_dict(obj) if obj else None})


@csrf_exempt
@require_http_methods(["POST"])
def update_laboratory_data(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    obj, _ = LaboratoryData.objects.get_or_create(id=0)
    for k, v in body.items():
        setattr(obj, k, v)
    obj.save()
    return JsonResponse({"updated": True})


@csrf_exempt
@require_http_methods(["POST"])
def add_laboratory_data(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    # copy row 0 with provided datetime
    src = LaboratoryData.objects.filter(id=0).first()
    if not src:
        return JsonResponse({"error": "baseline row id=0 not found"}, status=400)
    data = model_to_dict(src)
    data.pop("id", None)
    data["date_and_time"] = body.get("datetime")
    obj = LaboratoryData.objects.create(**data)
    return JsonResponse({"created": model_to_dict(obj)})


@require_http_methods(["GET"])
def get_historic_laboratory_data(request: HttpRequest):
    start = request.GET.get("start")
    end = request.GET.get("end")
    if not start or not end:
        return JsonResponse({"error": "start and end required"}, status=400)
    qs = LaboratoryData.objects.filter(id__gt=0, date_and_time__gte=start, date_and_time__lte=end)
    return JsonResponse({"results": [model_to_dict(o) for o in qs]})


@csrf_exempt
@require_http_methods(["POST"])
def delete_laboratory_data_record(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    hr_id = body.get("id")
    if not hr_id:
        return JsonResponse({"error": "id required"}, status=400)
    LaboratoryData.objects.filter(id=hr_id).delete()
    return JsonResponse({"deleted": True})
