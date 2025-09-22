from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..models import NewParametersAnalysisCategory
import json


@csrf_exempt
@require_http_methods(["POST"])
def add_new_parameter(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    parameter = (body.get("parameter") or "").replace(' ', '_')
    type_ = body.get("type")
    if not parameter or not type_:
        return JsonResponse({"error": "parameter and type required"}, status=400)
    NewParametersAnalysisCategory.objects.create(parameter=parameter, type=type_)
    return JsonResponse({"ok": True})


@require_http_methods(["GET"])
def get_new_parameters(request: HttpRequest):
    data = list(NewParametersAnalysisCategory.objects.all().values())
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"])
def delete_new_parameter(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    parameter = (body.get("parameter") or "").replace(' ', '_')
    if not parameter:
        return JsonResponse({"error": "parameter required"}, status=400)
    NewParametersAnalysisCategory.objects.filter(parameter=parameter).delete()
    return JsonResponse({"deleted": True})
