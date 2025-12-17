from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import BrixCalculatorData
import json


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_brix_calculator_data(request: HttpRequest):
    try:
        data = [model_to_dict(o) for o in BrixCalculatorData.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).order_by("tc")]
        return JsonResponse({"message": "✅ Datos obtenidos", "results": data})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener datos", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST", "PATCH"])
@jwt_required
@sensitive_endpoint
@log_api_access
def update_brix_calculator_data(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        valor_numerico = body.get("valor_numerico")
        columna = body.get("columna")
        fila = body.get("fila")
        resultado = body.get("resultado")
        
        if valor_numerico is None or columna is None or fila is None or resultado is None:
            return JsonResponse({
                "message": "❌ Campos requeridos: valor_numerico, columna, fila, resultado", 
                "error": "valor_numerico, columna, fila, resultado required"
            }, status=400)
        
        # Match local: Get tc from row offset
        # SELECT tc FROM brix_calculator_data ORDER BY tc LIMIT 1 OFFSET fila
        try:
            tc_obj = BrixCalculatorData.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).order_by("tc")[fila]
            tc_valor = tc_obj.tc
        except IndexError:
            return JsonResponse({"message": "❌ Fila no encontrada", "error": "Row not found"}, status=404)
        
        # Match local: Determine field based on column (1=pureza, 2=ss)
        if columna == 1:
            campo_actualizar = "pureza"
        elif columna == 2:
            campo_actualizar = "ss"
        else:
            return JsonResponse({"message": "❌ Columna inválida (debe ser 1 o 2)", "error": "Invalid column"}, status=400)
        
        # Match local: UPDATE brix_calculator_data SET {campo} = valor_numerico, brx = resultado WHERE tc = tc_valor
        update_data = {
            campo_actualizar: valor_numerico,
            "brx": resultado
        }
        
        updated = BrixCalculatorData.objects.filter(tc=tc_valor, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(**update_data)
        
        if not updated:
            return JsonResponse({"message": "❌ No se pudo actualizar", "error": "Update failed"}, status=500)
        
        obj = BrixCalculatorData.objects.get(tc=tc_valor, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1))
        return JsonResponse({"message": "✅ Datos actualizados", "updated": model_to_dict(obj)})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar", "error": str(e)}, status=500)
