from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import ProcessCodeData
import json


@require_http_methods(["GET"])
@jwt_required
@permission_required('read')
@log_api_access
def get_process_code_data(request: HttpRequest):
    data = [model_to_dict(o) for o in ProcessCodeData.objects.all().order_by("process")]
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def update_process_code_data(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    process = body.get("process")
    code = body.get("code")
    if process is None or code is None:
        return JsonResponse({"error": "process and code required"}, status=400)
    obj, _ = ProcessCodeData.objects.get_or_create(process=process)
    obj.code = code
    obj.save()
    return JsonResponse({"updated": model_to_dict(obj)})
