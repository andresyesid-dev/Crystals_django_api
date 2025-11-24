from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from ..models import Activation
from pbkdf2 import crypt
import json


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@log_api_access
def validate_software(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        given_code = body.get("code")
        if not given_code:
            return JsonResponse({"message": "❌ Código requerido", "ok": False}, status=400)
        
        # Match local implementation: get activation record with id=1
        act = Activation.objects.filter(id=1).first()
        if not act:
            return JsonResponse({"message": "❌ No existe registro de activación", "ok": False}, status=404)
        
        # Match local implementation: use pbkdf2 to validate
        validation_code = act.validation_code
        if validation_code == crypt(given_code, validation_code):
            # Update validated to 1
            Activation.objects.filter(id=1).update(validated=1)
            return JsonResponse({"message": "✅ Software activado exitosamente", "ok": True})
        
        return JsonResponse({"message": "❌ Código inválido", "ok": False})
    except Exception as e:
        return JsonResponse({"message": "❌ Error en validación", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@jwt_required
@log_api_access
def check_if_software_is_active(request: HttpRequest):
    try:
        # Match local implementation: get activation record with id=1
        act = Activation.objects.filter(id=1).first()
        if not act:
            return JsonResponse({"message": "⚠️ Sin registro de activación", "active": False})
        
        is_active = bool(int(act.validated) == 1)
        return JsonResponse({"message": "✅ Estado obtenido", "active": is_active})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al verificar estado", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def insert_default_activation(request: HttpRequest):
    """
    Inserts default activation record if none exists.
    This ensures the activation table has the initial record with the default validation code.
    """
    try:
        # Check if activation already exists
        if Activation.objects.exists():
            activation = Activation.objects.first()
            return JsonResponse({
                "message": "⚠️ Registro de activación ya existe",
                "result": {
                    "id": activation.id,
                    "validation_code": activation.validation_code,
                    "validated": activation.validated
                }
            })
        
        # Create default activation with the same hash as SQLite
        activation = Activation.objects.create(
            validation_code='$p5k2$$lDD.2q8l$FSS9CFIP2YEihV.qk4W1oVD2NO6z3Vzn',
            validated=0
        )
        
        return JsonResponse({
            "message": "✅ Registro de activación creado exitosamente",
            "created": {
                "id": activation.id,
                "validation_code": activation.validation_code,
                "validated": activation.validated
            }
        }, status=201)
        
    except Exception as e:
        import traceback
        return JsonResponse({
            "message": "❌ Error al crear registro de activación",
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status=500)
