from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import ManualMeasurement
import json


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def select_manual_measurements(request: HttpRequest):
    try:
        data = [model_to_dict(m) for m in ManualMeasurement.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).order_by("id")]
        return JsonResponse({"message": "✅ Mediciones manuales obtenidas exitosamente", "results": data})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener mediciones manuales", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def add_manual_measurement(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        time = body.get("time")
        value = body.get("value")
        if time is None or value is None:
            return JsonResponse({"message": "❌ Los campos 'time' y 'value' son requeridos", "error": "time and value required"}, status=400)
        obj = ManualMeasurement.objects.create(time=time, value=value, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1))
        return JsonResponse({"message": "✅ Medición manual agregada exitosamente", "created": model_to_dict(obj)}, status=201)
    except Exception as e:
        return JsonResponse({"message": "❌ Error al agregar medición manual", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"]) 
@jwt_required
@log_api_access
def clear_manual_measurement_db(request: HttpRequest):
    try:
        ManualMeasurement.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).delete()
        return JsonResponse({"message": "✅ Base de datos de mediciones manuales limpiada exitosamente", "cleared": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al limpiar base de datos", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PATCH"])
@jwt_required
@sensitive_endpoint
@log_api_access
def update_manual_measurement(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        measurement_id = body.get("measurement_id")
        time = body.get("time")
        value = body.get("value")
        
        if measurement_id is None:
            return JsonResponse({"message": "❌ El campo 'measurement_id' es requerido", "error": "measurement_id required"}, status=400)
        
        # Match local: UPDATE manual_measurements SET time=:time, value=:value WHERE id=:id
        updated = ManualMeasurement.objects.filter(id=measurement_id, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(
            time=time,
            value=value
        )
        
        if not updated:
            return JsonResponse({"message": "❌ Medición no encontrada", "error": "Measurement not found"}, status=404)
        
        obj = ManualMeasurement.objects.get(id=measurement_id, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1))
        return JsonResponse({"message": "✅ Medición manual actualizada exitosamente", "updated": model_to_dict(obj)})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar medición manual", "error": str(e)}, status=500)

