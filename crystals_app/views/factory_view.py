from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from ..models import CredentialsFactory
from ..decorators import rate_limit_protected, log_api_access
import bcrypt
import json


@csrf_exempt
@require_http_methods(["POST"])
@rate_limit_protected(rate='5/m')  # Limita intentos de login de fábrica
@log_api_access
def validate_factory_credentials(request: HttpRequest):
    """
    Login de fábrica en la nube.

    El cliente (Crystals3.0) envía SOLO la contraseña en texto plano y NO manda
    X-Factory-ID (justamente la fábrica es lo que se está averiguando). Se
    recorren TODAS las filas de credentials_factory y se compara el hash bcrypt;
    la primera que coincide identifica la fábrica.

    Contrato esperado por el cliente (src/logic/factory_auth.py):
        200 {"factory_id": N}    -> la contraseña coincide con la fábrica N
        200 {"factory_id": null} -> ninguna fábrica coincide
        4xx/5xx/timeout          -> el cliente lo trata como "sin verificar"
                                    (AuthResult.VERIFICATION_ERROR, no penaliza)

    Por eso, ante un fallo real (excepción) se devuelve 500 — NUNCA un 200 con
    factory_id null, que el cliente leería como "contraseña incorrecta" y
    penalizaría al usuario por un problema de servidor.
    """
    try:
        body = json.loads(request.body or b"{}")
        password = body.get("password")
        if password is None or password == "":
            return JsonResponse(
                {"message": "❌ El campo 'password' es requerido",
                 "error": "password required"},
                status=400,
            )

        pwd_bytes = password.encode("utf-8")
        matched_factory_id = None
        for row in CredentialsFactory.objects.all():
            stored = row.password
            if not stored:
                continue
            try:
                if bcrypt.checkpw(pwd_bytes, stored.encode("utf-8")):
                    matched_factory_id = row.factory_id
                    break
            except ValueError:
                # Hash almacenado malformado: se ignora esa fila y se sigue
                # probando el resto, no se aborta toda la verificación.
                continue

        return JsonResponse(
            {"message": "✅ Validación de credenciales de fábrica completada",
             "factory_id": matched_factory_id}
        )
    except Exception as e:
        return JsonResponse(
            {"message": "❌ Error al validar credenciales de fábrica",
             "error": str(e)},
            status=500,
        )
