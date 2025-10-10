from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import LabMaterialsSettings
import json


@require_http_methods(["GET"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def get_lab_materials_settings(request: HttpRequest):
    data = [model_to_dict(o) for o in LabMaterialsSettings.objects.all()]
    return JsonResponse({"results": data})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def insert_lab_materials_settings(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    materials = body.get("materials") or []
    created = 0
    for item in materials:
        material = item if isinstance(item, str) else item.get("material")
        visible = 1 if (not isinstance(item, dict) or item.get("visible", 1)) else 1
        if material:
            LabMaterialsSettings.objects.get_or_create(material=material, defaults={"visible": visible})
            created += 1
    return JsonResponse({"ok": True, "created": created})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def update_lab_materials_settings(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    updates = body.get("updates") or []
    updated = 0
    for item in updates:
        material = item.get("material")
        visible = item.get("visible")
        if material is not None and visible is not None:
            updated += LabMaterialsSettings.objects.filter(material=material).update(visible=int(bool(visible)))
    return JsonResponse({"ok": True, "updated": updated})
