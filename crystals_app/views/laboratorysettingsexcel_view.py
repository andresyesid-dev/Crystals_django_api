from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import LaboratorySettingsExcel
import json


@require_http_methods(["GET"])
@jwt_required
@sensitive_endpoint
@log_api_access
def get_laboratory_settings_excel_letters(request: HttpRequest):
    try:
        obj = LaboratorySettingsExcel.objects.filter(id=0).first()
        if not obj:
            return JsonResponse({"message": "✅ Configuración Excel de laboratorio (letras) obtenida", "result": None})
        data = model_to_dict(obj)
        return JsonResponse({"message": "✅ Configuración Excel de laboratorio (letras) obtenida exitosamente", "result": {k: v for k, v in data.items() if k.endswith('_letter')}})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener configuración Excel (letras)", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@sensitive_endpoint
@log_api_access
def get_laboratory_settings_excel_numbers(request: HttpRequest):
    try:
        obj = LaboratorySettingsExcel.objects.filter(id=0).first()
        if not obj:
            return JsonResponse({"message": "✅ Configuración Excel de laboratorio (números) obtenida", "result": None})
        data = model_to_dict(obj)
        return JsonResponse({"message": "✅ Configuración Excel de laboratorio (números) obtenida exitosamente", "result": {k: v for k, v in data.items() if k.endswith('_number')}})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener configuración Excel (números)", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST", "PATCH"])
@jwt_required
@sensitive_endpoint
@log_api_access
def update_laboratory_settings_excel(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        obj, _ = LaboratorySettingsExcel.objects.get_or_create(id=0)
        for k, v in body.items():
            setattr(obj, k, v)
        obj.save()
        return JsonResponse({"message": "✅ Configuración Excel de laboratorio actualizada exitosamente", "updated": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar configuración Excel", "error": str(e)}, status=500)
