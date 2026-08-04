from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from django.db import transaction
from ..models import EnableAditionalRanges
from ..decorators import jwt_required, log_api_access, sensitive_endpoint
from ..cache_utils import cached_per_factory, bump_cache_version
import json

_CACHE_GROUP = 'enable_aditional_ranges'


def _parse_json(request: HttpRequest):
    try:
        return json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        return {}


@require_http_methods(["GET"])
@jwt_required
@log_api_access
@cached_per_factory(_CACHE_GROUP)
def list_enable_aditional_ranges(request: HttpRequest):
    try:
        factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
        qs = EnableAditionalRanges.objects.filter(factory_id=factory_id).order_by("calibration")
        data = [model_to_dict(o) for o in qs]
        return JsonResponse({"message": "✅ Configuración obtenida", "results": data})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener configuración", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@log_api_access
@sensitive_endpoint
def save_enable_aditional_ranges(request: HttpRequest):
    """
    Upsert del estado enable por calibración.
    Payload: {'items': [{'calibration': <name>, 'enable': 0|1}, ...]}
    Sincroniza la tabla al conjunto de items recibido para esta fábrica:
    - calibraciones presentes -> se crean/actualizan con su enable.
    - calibraciones ausentes en items -> se eliminan (ya no existen).
    """
    try:
        factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
        payload = _parse_json(request)
        items = payload.get("items", [])

        with transaction.atomic():
            incoming_names = set()
            for item in items:
                name = item.get("calibration")
                if not name:
                    continue
                enable = 1 if item.get("enable", 1) else 0
                incoming_names.add(name)
                EnableAditionalRanges.objects.update_or_create(
                    calibration=name,
                    factory_id=factory_id,
                    defaults={"enable": enable},
                )
            # Limpiar filas de calibraciones que ya no existen
            EnableAditionalRanges.objects.filter(factory_id=factory_id).exclude(
                calibration__in=incoming_names
            ).delete()

        bump_cache_version(_CACHE_GROUP, factory_id)
        return JsonResponse({"message": "✅ Configuración guardada", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al guardar configuración", "error": str(e)}, status=500)
