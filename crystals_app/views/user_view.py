from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from ..models import User
from ..decorators import rate_limit_protected, log_api_access, jwt_required, permission_required, sensitive_endpoint
from pbkdf2 import crypt
import json


@csrf_exempt
@require_http_methods(["POST"])
@rate_limit_protected(rate='5/m')  # Limit login attempts
@log_api_access
def validate_user_credentials(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        username = body.get("username")
        password = body.get("password")
        if not username or password is None:
            return JsonResponse({"message": "❌ Los campos 'username' y 'password' son requeridos", "ok": False, "error": "username and password required"}, status=400)
        
        u = User.objects.filter(username=username).first()
        if not u:
            return JsonResponse({"message": "✅ Validación de credenciales completada", "ok": False})
        
        # Match local implementation: use pbkdf2 to validate hashed password
        is_valid = u.password == crypt(password, u.password)
        return JsonResponse({"message": "✅ Validación de credenciales completada", "ok": is_valid})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al validar credenciales de usuario", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def create_user(request: HttpRequest):
    """
    Creates a new user in the database.
    Used for creating default admin user during database initialization.
    """
    try:
        body = json.loads(request.body or b"{}")
        username = body.get("username")
        password = body.get("password")
        
        if not username or not password:
            return JsonResponse({
                "message": "❌ Los campos 'username' y 'password' son requeridos",
                "error": "username and password required"
            }, status=400)
        
        # Check if user already exists
        existing_user = User.objects.filter(username=username).first()
        if existing_user:
            return JsonResponse({
                "message": "ℹ️ Usuario ya existe",
                "ok": True,
                "already_exists": True
            })
        
        # Create new user
        User.objects.create(username=username, password=password)
        
        return JsonResponse({
            "message": "✅ Usuario creado exitosamente",
            "ok": True,
            "created": True
        })
    except Exception as e:
        return JsonResponse({
            "message": "❌ Error al crear usuario",
            "error": str(e)
        }, status=500)
