from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import Company
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
import json


@require_http_methods(["GET"])
@jwt_required
@permission_required('read')
@log_api_access
def get_company(request: HttpRequest):
    obj = Company.objects.first()
    return JsonResponse({"result": model_to_dict(obj) if obj else None})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('admin')
@log_api_access
@sensitive_endpoint
def update_company_name(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    name = body.get("name")
    if name is None:
        return JsonResponse({"error": "name required"}, status=400)
    obj, _ = Company.objects.get_or_create(id=1, defaults={"name": name, "logo": ""})
    obj.name = name
    obj.save()
    return JsonResponse({"updated": True})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('admin')
@log_api_access
@sensitive_endpoint
def update_company_logo(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    logo = body.get("logo")
    if logo is None:
        return JsonResponse({"error": "logo required"}, status=400)
    obj, _ = Company.objects.get_or_create(id=1, defaults={"name": "", "logo": logo})
    obj.logo = logo
    obj.save()
    return JsonResponse({"updated": True})
