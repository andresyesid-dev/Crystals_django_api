from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import LaboratorySettingsExcel
import json


def _parse_json(request: HttpRequest):
    try:
        return json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        return {}


@require_http_methods(["GET"])
@jwt_required
@sensitive_endpoint
@log_api_access
def get_laboratory_settings_excel_letters(request: HttpRequest):
    try:
        obj = LaboratorySettingsExcel.objects.filter(id=0, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).first()
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
        obj = LaboratorySettingsExcel.objects.filter(id=0, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).first()
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
        payload = _parse_json(request)
        # Handle wrapped payload {'data': {...}}
        data = payload.get("data", payload)
        obj, created = LaboratorySettingsExcel.objects.get_or_create(id=0, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1))
        
        # Update fields
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        
        obj.save()
        print("✅ LaboratorySettingsExcel saved successfully")
        
        return JsonResponse({"message": "✅ Configuración actualizada exitosamente", "ok": True})
    except Exception as e:
        print(f"❌ update_laboratory_settings_excel error: {e}")
        return JsonResponse({"message": "❌ Error al actualizar configuración", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@sensitive_endpoint
@log_api_access
def get_laboratory_settings_excel(request: HttpRequest):
    try:
        obj = LaboratorySettingsExcel.objects.filter(id=0, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).first()
        if not obj:
            return JsonResponse({"message": "✅ Configuración Excel de laboratorio obtenida", "result": None})
        data = model_to_dict(obj)
        return JsonResponse({"message": "✅ Configuración Excel de laboratorio obtenida exitosamente", "result": data})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener configuración Excel", "error": str(e)}, status=500)
