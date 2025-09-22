from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import GlobalSetting
import json


@require_http_methods(["GET"])
def get_line_color(request: HttpRequest):
    gs = GlobalSetting.objects.first()
    return JsonResponse({"line_color": gs.line_color if gs else None})


@csrf_exempt
@require_http_methods(["POST"])
def update_line_color(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    color = body.get("line_color")
    if not color:
        return JsonResponse({"error": "line_color required"}, status=400)
    obj, _ = GlobalSetting.objects.get_or_create(id=1, defaults={"line_color": color})
    obj.line_color = color
    obj.save()
    return JsonResponse({"updated": True, "object": model_to_dict(obj)})
