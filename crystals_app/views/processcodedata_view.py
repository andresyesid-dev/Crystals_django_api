from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import ProcessCodeData
import json


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_process_code_data(request: HttpRequest):
    try:
        data = [model_to_dict(o) for o in ProcessCodeData.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).order_by("process")]
        return JsonResponse({"message": "✅ Códigos de proceso obtenidos exitosamente", "results": data})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener códigos de proceso", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST", "PATCH"])
@jwt_required
@sensitive_endpoint
@log_api_access
def update_process_code_data(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        new_value = body.get("new_value")
        fila = body.get("fila")
        
        if new_value is None or fila is None:
            return JsonResponse({
                "message": "❌ Los campos 'new_value' y 'fila' son requeridos", 
                "error": "new_value and fila required"
            }, status=400)
        
        # Match local: Get process from row offset
        # SELECT process FROM process_code_data ORDER BY process LIMIT 1 OFFSET fila
        try:
            qs = ProcessCodeData.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).order_by("process")
            if fila >= qs.count():
                return JsonResponse({"message": "❌ Fila no encontrada (índice fuera de rango)", "error": "Row index out of range"}, status=404)
                
            process_obj = qs[fila]
            process_valor = process_obj.process
        except IndexError:
            return JsonResponse({"message": "❌ Fila no encontrada", "error": "Row not found"}, status=404)
        except Exception as e:
            return JsonResponse({"message": "❌ Error buscando proceso", "error": str(e)}, status=500)
        
        # Match local: UPDATE process_code_data SET code = new_value WHERE process = process_valor
        updated = ProcessCodeData.objects.filter(process=process_valor, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(code=new_value)
        
        if not updated:
            return JsonResponse({"message": "❌ No se pudo actualizar", "error": "Update failed"}, status=500)
        
        obj = ProcessCodeData.objects.filter(process=process_valor, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).first()
        return JsonResponse({"message": "✅ Código de proceso actualizado exitosamente", "updated": model_to_dict(obj) if obj else {}})
    except json.JSONDecodeError:
        return JsonResponse({"message": "❌ JSON inválido", "error": "Invalid JSON"}, status=400)
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Print to server logs
        return JsonResponse({
            "message": "❌ Error al actualizar código de proceso", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status=500)
