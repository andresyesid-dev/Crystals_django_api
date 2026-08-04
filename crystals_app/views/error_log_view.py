from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..models import ErrorLog
from ..decorators import jwt_required, log_api_access, rate_limit_protected
import json

# Topes de tamaño: un cliente en bucle de error no debe poder mandar payloads
# gigantes ni llenar la tabla con tracebacks kilométricos. Los VARCHAR se
# truncan a su límite de columna porque PostgreSQL (a diferencia de SQLite)
# rechaza con DataError cualquier valor que exceda el max_length.
_MAX_TRACEBACK = 20000
_MAX_MENSAJE = 10000


def _trunc(value, limit):
    if value is None:
        return None
    return str(value)[:limit]


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@rate_limit_protected(rate='30/m')  # tope ante bucles de error del cliente
@log_api_access
def add_error_log(request: HttpRequest):
    """
    Recibe un error del desktop (F5.15, fase Online) y lo persiste en la tabla
    centralizada `error_log` de Supabase.

    Filosofía TOLERANTE: este endpoint nunca rechaza un error por venir
    incompleto o malformado — se guarda lo que haya llegado. Rechazar el
    registro de un error dejaría al ingenio sin historial justo cuando más
    se necesita. La única respuesta de fallo (500) es si la BD misma no
    acepta la escritura; en ese caso el cliente (_dual_write) cae a su
    SQLite local (LOCAL_ONLY) y el error no se pierde.
    """
    try:
        try:
            body = json.loads(request.body or b"{}")
            if not isinstance(body, dict):
                body = {}
        except (ValueError, TypeError):
            body = {}

        obj = ErrorLog.objects.create(
            factory_id=request.META.get('HTTP_X_FACTORY_ID', 1),
            fecha_hora=_trunc(body.get("fecha_hora"), 50),
            tipo_error=_trunc(body.get("tipo_error"), 100),
            mensaje=_trunc(body.get("mensaje"), _MAX_MENSAJE),
            traceback=_trunc(body.get("traceback"), _MAX_TRACEBACK),
            contexto=_trunc(body.get("contexto"), 255),
            modo=_trunc(body.get("modo"), 10),
            version_app=_trunc(body.get("version_app"), 20),
            # recibido_en lo llena el servidor (auto_now_add): referencia
            # temporal confiable aunque el reloj de la PC del ingenio esté mal.
        )
        return JsonResponse({"message": "✅ Error registrado", "ok": True, "id": obj.id})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al registrar el error", "error": str(e)}, status=500)
