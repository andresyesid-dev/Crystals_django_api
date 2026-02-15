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
        factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
        # Fetch the first record associated with this factory
        obj = LaboratoryData.objects.filter(factory_id=factory_id).order_by('id').first()
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
        factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
        
        # Find the FIRST record for this factory (ordered by ID)
        obj = LaboratoryData.objects.filter(factory_id=factory_id).order_by('id').first()
        
        if not obj:
            # If no record exists, create one
            # Rely on AutoIncrement for ID
            obj = LaboratoryData(factory_id=factory_id)
            # We will save it after setting attributes below

        for k, v in body.items():
            # Prevent overwriting critical ID/Factory fields just in case
            if k not in ['id', 'factory_id']:
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
        # Determine data source
        data = {}
        # Checks if 'data' key exists (from our updated client) or if body is flat
        if 'data' in body and isinstance(body['data'], dict):
             # Client sent {'datetime': ..., 'data': {...}, 'factory_id': ...}
             data = body['data'].copy()
             data['date_and_time'] = body.get('datetime')
        elif len(body) > 2: 
             # Client sent flat dict
             data = body.copy()
             if 'datetime' in data:
                data['date_and_time'] = data.pop('datetime')
        else:
             # Legacy fallback: copy from LATEST record for this factory
             factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
             latest = LaboratoryData.objects.filter(factory_id=factory_id).order_by('-id').first()
             if latest:
                 data = model_to_dict(latest)
                 data.pop('id', None) # Remove old ID
             else:
                 data = {}
             
             if 'datetime' in body:
                 data['date_and_time'] = body['datetime']

        # Enforce Factory
        data['factory_id'] = request.META.get('HTTP_X_FACTORY_ID', 1)
        # Ensure we don't accidentally pass an ID if it came in the body/copy
        data.pop('id', None)
        
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
        
        # Check if ANY record exists for this factory
        if LaboratoryData.objects.filter(factory_id=factory_id).exists():
             return JsonResponse({"message": "⚠️ Ya existen registros para esta fábrica", "ok": True})
        
        # Rely on AutoField (AutoIncrement) for ID generation to ensure correctness and concurrency safety.
        # This guarantees the new ID is always Max + 1 (or next in sequence).
        
        default_data = {
            "factory_id": factory_id,
            "date_and_time": "..."
        }
        
        # Populate other fields with "..." where possible
        for field in LaboratoryData._meta.fields:
            if field.name not in ["id", "factory_id", "date_and_time"]:
                 if field.get_internal_type() in ['CharField', 'TextField']:
                     default_data[field.name] = "..."
                 else:
                     pass

        obj = LaboratoryData.objects.create(**default_data)
        return JsonResponse({"message": "✅ Registro por defecto creado exitosamente", "ok": True, "new_id": obj.id})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al crear registro por defecto", "error": str(e)}, status=500)
