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
