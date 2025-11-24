from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import Company
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
import json


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_company(request: HttpRequest):
    try:
        # Match local implementation: get company with id=1
        obj = Company.objects.filter(id=1).first()
        return JsonResponse({"message": "✅ Datos de compañía obtenidos", "result": model_to_dict(obj) if obj else None})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener datos de compañía", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST", "PATCH"])
@jwt_required
@log_api_access
@sensitive_endpoint
def update_company_name(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        name = body.get("name")
        if name is None:
            return JsonResponse({"message": "❌ El campo 'name' es requerido", "error": "name required"}, status=400)
        # Match local implementation: direct update on id=1
        Company.objects.filter(id=1).update(name=name)
        return JsonResponse({"message": "✅ Nombre de compañía actualizado", "updated": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar nombre", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST", "PATCH"])
@jwt_required
@log_api_access
@sensitive_endpoint
def update_company_logo(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        logo = body.get("logo")
        if logo is None:
            return JsonResponse({"message": "❌ El campo 'logo' es requerido", "error": "logo required"}, status=400)
        # Match local implementation: direct update on id=1
        Company.objects.filter(id=1).update(logo=logo)
        return JsonResponse({"message": "✅ Logo de compañía actualizado", "updated": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar logo", "error": str(e)}, status=500)
