from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import GlobalSetting
import json


@require_http_methods(["GET"])
@jwt_required
@permission_required('read')
@log_api_access
def get_line_color(request: HttpRequest):
    gs = GlobalSetting.objects.first()
    return JsonResponse({"line_color": gs.line_color if gs else None})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def update_line_color(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    color = body.get("line_color")
    if not color:
        return JsonResponse({"error": "line_color required"}, status=400)
    obj, _ = GlobalSetting.objects.get_or_create(id=1, defaults={"line_color": color})
    obj.line_color = color
    obj.save()
    return JsonResponse({"updated": True, "object": model_to_dict(obj)})
