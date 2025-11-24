from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import RefinoCalculation
import json


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_refino_calculations(request: HttpRequest):
    try:
        data = [model_to_dict(o) for o in RefinoCalculation.objects.all()]
        return JsonResponse({"message": "✅ Cálculos de refino obtenidos exitosamente", "results": data})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener cálculos de refino", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def insert_refino_calculations(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        field_name = body.get("field_name")
        field_value = body.get("field_value")
        
        if not field_name:
            return JsonResponse({"message": "❌ El campo 'field_name' es requerido", "error": "field_name required"}, status=400)
        
        # Match local: Check if row exists, UPDATE if yes, INSERT if no
        count = RefinoCalculation.objects.count()
        
        if count > 0:
            # UPDATE existing row (first row)
            first_obj = RefinoCalculation.objects.first()
            if field_value is not None:
                setattr(first_obj, field_name, field_value)
            else:
                setattr(first_obj, field_name, None)
            first_obj.save()
            return JsonResponse({"message": "✅ Cálculo de refino actualizado", "updated": True})
        else:
            # INSERT new row
            RefinoCalculation.objects.create(**{field_name: field_value})
            return JsonResponse({"message": "✅ Cálculo de refino insertado", "created": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al insertar/actualizar cálculo de refino", "error": str(e)}, status=500)
