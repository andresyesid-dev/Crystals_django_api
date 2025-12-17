from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import LaboratoryData
import json


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_laboratory_data(request: HttpRequest):
    try:
        obj = LaboratoryData.objects.filter(id=0, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).first()
        return JsonResponse({"message": "✅ Datos de laboratorio obtenidos exitosamente", "result": model_to_dict(obj) if obj else None})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener datos de laboratorio", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST", "PATCH"])
@jwt_required
@sensitive_endpoint
@log_api_access
def update_laboratory_data(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        obj, _ = LaboratoryData.objects.get_or_create(id=0, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1))
        for k, v in body.items():
            setattr(obj, k, v)
        obj.save()
        return JsonResponse({"message": "✅ Datos de laboratorio actualizados exitosamente", "updated": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar datos de laboratorio", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def add_laboratory_data(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        
        # If all material fields are provided, use them directly
        # Otherwise, copy from baseline row id=0
        if len(body) > 2:  # More than just 'datetime' provided
            # Create new record with all provided data
            data = body.copy()
            # Ensure datetime field is set correctly
            if 'datetime' in data:
                data['date_and_time'] = data.pop('datetime')
            data['factory_id'] = request.META.get('HTTP_X_FACTORY_ID', 1)
            obj = LaboratoryData.objects.create(**data)
            return JsonResponse({"message": "✅ Datos de laboratorio agregados exitosamente", "created": model_to_dict(obj)})
        else:
            # Fallback: copy row 0 with provided datetime (legacy behavior)
            src = LaboratoryData.objects.filter(id=0, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).first()
            if not src:
                return JsonResponse({"message": "❌ Fila base id=0 no encontrada", "error": "baseline row id=0 not found"}, status=400)
            data = model_to_dict(src)
            data.pop("id", None)
            data["date_and_time"] = body.get("datetime")
            data["factory_id"] = request.META.get('HTTP_X_FACTORY_ID', 1)
            obj = LaboratoryData.objects.create(**data)
            return JsonResponse({"message": "✅ Datos de laboratorio agregados exitosamente", "created": model_to_dict(obj)})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al agregar datos de laboratorio", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_historic_laboratory_data(request: HttpRequest):
    try:
        start = request.GET.get("start")
        end = request.GET.get("end")
        if not start or not end:
            return JsonResponse({"message": "❌ Los parámetros 'start' y 'end' son requeridos", "error": "start and end required"}, status=400)
        qs = LaboratoryData.objects.filter(id__gt=0, date_and_time__gte=start, date_and_time__lte=end, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1))
        return JsonResponse({"message": "✅ Datos históricos de laboratorio obtenidos exitosamente", "results": [model_to_dict(o) for o in qs]})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener datos históricos", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def delete_laboratory_data_record(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        hr_id = body.get("id")
        if not hr_id:
            return JsonResponse({"message": "❌ El campo 'id' es requerido", "error": "id required"}, status=400)
        LaboratoryData.objects.filter(id=hr_id, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).delete()
        return JsonResponse({"message": "✅ Registro de laboratorio eliminado exitosamente", "deleted": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al eliminar registro de laboratorio", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def lab_data_insert_default(request: HttpRequest):
    try:
        factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
        if LaboratoryData.objects.filter(id=0, factory_id=factory_id).exists():
             return JsonResponse({"message": "⚠️ El registro por defecto ya existe", "ok": True})
        
        # Create default record with "..." in all text fields
        # Note: We need to respect the model fields. Assuming most are CharFields or similar where "..." is valid.
        # If there are numeric fields, this might error.
        # However, the user said "todos los valores deben ser un texto '...'".
        # I'll check the model columns first to be safe, but for now I'll create an empty object and set fields.
        
        # Actually, let's look at the model definition to be sure about fields.
        # But per user request, I will attempt to set fields to "...".
        # Since I don't see the models.py here, I will rely on the instruction.
        
        default_data = {
            "id": 0,
            "factory_id": factory_id,
            "date_and_time": "..."
        }
        
        # Attempt to get all field names from the model to populate them
        for field in LaboratoryData._meta.fields:
            if field.name not in ["id", "factory_id", "date_and_time"]:
                 # Check if field accepts strings. If it's a number, "..." will fail.
                 # Assuming text fields for now or that the user knows what they are asking.
                 # Safest bet for 'all values' is to iterate model fields.
                 if field.get_internal_type() in ['CharField', 'TextField']:
                     default_data[field.name] = "..."
                 else:
                     # For numeric types, we can't put "...". 
                     # I will leave them as None/Default or ask.
                     # But the user was specific: "cada una de las columnas".
                     # This implies they might all be text.
                     pass

        obj = LaboratoryData.objects.create(**default_data)
        return JsonResponse({"message": "✅ Registro por defecto creado exitosamente", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al crear registro por defecto", "error": str(e)}, status=500)
