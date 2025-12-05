from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from django.db import transaction
from ..models import Calibration, ProcessCodeData, HistoricReport
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
import json


def _parse_json(request: HttpRequest):
    try:
        return json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        return {}


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def select_calibrations(request: HttpRequest):
    try:
        # Match local implementation: order by active desc, ordering asc
        qs = Calibration.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).order_by("-active", "ordering")
        data = [model_to_dict(o) for o in qs]
        return JsonResponse({"message": "✅ Calibraciones obtenidas", "results": data})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener calibraciones", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def select_historic_reports_calibrations(request: HttpRequest):
    try:
        # Filtered by ordering not null, ordered by ordering asc
        data = [model_to_dict(o) for o in Calibration.objects.filter(ordering__isnull=False, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).order_by("ordering")]
        return JsonResponse({"message": "✅ Calibraciones históricas obtenidas", "results": data})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener calibraciones", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def select_excluded_reports_calibrations(request: HttpRequest):
    try:
        # Filtered by ordering null, ordered by name
        data = [model_to_dict(o) for o in Calibration.objects.filter(ordering__isnull=True, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).order_by("name")]
        return JsonResponse({"message": "✅ Calibraciones excluidas obtenidas", "results": data})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener calibraciones excluidas", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def select_active_calibration(request: HttpRequest):
    try:
        c = Calibration.objects.filter(active=1, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).first()
        return JsonResponse({"message": "✅ Calibración activa obtenida", "result": model_to_dict(c) if c else None})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener calibración activa", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
def set_calibration_as_active(request: HttpRequest):
    try:
        payload = _parse_json(request)
        name = payload.get("name")
        if not name:
            return JsonResponse({"message": "❌ El campo 'name' es requerido", "error": "name is required"}, status=400)
        with transaction.atomic():
            Calibration.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(active=0)
            Calibration.objects.filter(name=name, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(active=1)
        return JsonResponse({"message": "✅ Calibración activada exitosamente", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al activar calibración", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@log_api_access
@sensitive_endpoint
def create_calibration(request: HttpRequest):
    try:
        payload = _parse_json(request)
        
        # El cliente envía: {'values': {...}, 'ordering': ...}
        # Extraer values del payload
        values_dict = payload.get("values", payload)  # Si no hay 'values', usar payload directo
        ordering = payload.get("ordering")
        
        # Validar campos requeridos
        name = values_dict.get("name")
        if not name:
            # Log para debug
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Create calibration failed - missing 'name'. Payload: {payload}")
            
            return JsonResponse({
                "message": "❌ El campo 'name' es requerido", 
                "error": "name is required"
            }, status=400)
        
        # Construir campos desde values_dict
        fields = {
            "name": name,
            "pixels_per_metric": values_dict.get("pixels_per_metric", 1.0),
            "metric_name": values_dict.get("metric_name", "mm"),
            "range": values_dict.get("range", "0-100"),
            "active": values_dict.get("active", 0),
            "powder": values_dict.get("powder"),
            "ordering": ordering if ordering is not None else values_dict.get("ordering"),
            "target_cv": values_dict.get("target_cv"),
            "target_mean": values_dict.get("target_mean")
        }
        
        # Allow explicit ID if provided (e.g. for imports)
        explicit_id = payload.get("id") or values_dict.get("id")
        if explicit_id:
            fields["id"] = explicit_id
        
        # Match local implementation: create in both tables within transaction
        with transaction.atomic():
            # First insert into process_code_data
            ProcessCodeData.objects.create(process=name, code='...', factory_id=request.META.get('HTTP_X_FACTORY_ID', 1))
            
            # Then create calibration
            fields["factory_id"] = request.META.get('HTTP_X_FACTORY_ID', 1)
            obj = Calibration.objects.create(**fields)
        
        return JsonResponse({"message": "✅ Calibración creada exitosamente", "created": model_to_dict(obj)}, status=201)
    except Exception as e:
        import traceback
        return JsonResponse({
            "message": "❌ Error al crear calibración", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status=500)


@csrf_exempt
@require_http_methods(["POST", "PATCH"])
@jwt_required
@log_api_access
@sensitive_endpoint
def update_calibration(request: HttpRequest):
    """
    Actualiza una calibración existente.
    Requiere 'id' y 'values' en el payload.
    """
    try:
        payload = _parse_json(request)
        calibration_id = payload.get("id") or payload.get("calibration_id")
        values = payload.get("values", {})
        
        if not calibration_id:
            return JsonResponse({
                "message": "❌ Se requiere 'id' o 'calibration_id'", 
                "error": "calibration_id required"
            }, status=400)
        
        # Match local implementation: get old name first
        try:
            obj = Calibration.objects.get(id=calibration_id, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1))
            old_name = obj.name
        except Calibration.DoesNotExist:
            return JsonResponse({
                "message": "❌ Calibración no encontrada",
                "error": "Calibration not found"
            }, status=404)
        
        # Update within transaction (match local behavior)
        with transaction.atomic():
            # If name is changing, update process_code_data
            new_name = values.get("name")
            if new_name and new_name != old_name:
                ProcessCodeData.objects.filter(process=old_name, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(process=new_name)
            
            # Update calibration fields
            updatable_fields = {
                "name", "pixels_per_metric", "metric_name", "range", 
                "target_cv", "target_mean", "powder"
            }
            for field in updatable_fields:
                if field in values:
                    setattr(obj, field, values[field])
            obj.save()
        
        return JsonResponse({
            "message": "✅ Calibración actualizada exitosamente",
            "result": model_to_dict(obj)
        })
    except Exception as e:
        import traceback
        return JsonResponse({
            "message": "❌ Error al procesar calibración",
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@log_api_access
@sensitive_endpoint
def delete_calibration(request: HttpRequest):
    try:
        payload = _parse_json(request)
        calibration_id = payload.get("id") or payload.get("calibration_id")
        if not calibration_id:
            return JsonResponse({"message": "❌ El campo 'id' es requerido", "error": "id is required"}, status=400)
        
        # Match local implementation: 4 steps
        try:
            calibration = Calibration.objects.get(id=calibration_id, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1))
            calibration_name = calibration.name
        except Calibration.DoesNotExist:
            return JsonResponse({"message": "❌ Calibración no encontrada", "error": "not found"}, status=404)
        
        with transaction.atomic():
            # 1. Update historic_reports to set calibration_id to NULL
            HistoricReport.objects.filter(calibration_fk_id=calibration_id, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(calibration_fk=None)
            
            # 2. Delete from process_code_data
            ProcessCodeData.objects.filter(process=calibration_name, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).delete()
            
            # 3. Delete calibration
            calibration.delete()
        
        return JsonResponse({"message": "✅ Calibración eliminada exitosamente", "deleted": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al eliminar calibración", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_calibration(request: HttpRequest):
    try:
        name = request.GET.get("name")
        if not name:
            return JsonResponse({"message": "❌ El parámetro 'name' es requerido", "error": "name is required"}, status=400)
        obj = Calibration.objects.filter(name=name, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).first()
        return JsonResponse({"message": "✅ Calibración obtenida", "result": model_to_dict(obj) if obj else None})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener calibración", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST", "PATCH"])
@jwt_required
@log_api_access
@sensitive_endpoint
def update_calibration_order(request: HttpRequest):
    """
    Actualiza el ordering de una calibración.
    """
    try:
        payload = _parse_json(request)
        calibration_id = payload.get("id") or payload.get("calibration_id")
        ordering = payload.get("ordering")
        
        if not calibration_id:
            print(f"❌ update_calibration_order failed: missing id. Payload: {payload}")
            return JsonResponse({"message": "❌ Se requiere 'id' o 'calibration_id'", "error": "calibration_id required"}, status=400)
        
        if ordering is None:
            print(f"❌ update_calibration_order failed: missing ordering. Payload: {payload}")
            return JsonResponse({"message": "❌ Se requiere el campo 'ordering'", "error": "ordering required"}, status=400)
        
        # Match local implementation: direct update
        Calibration.objects.filter(id=calibration_id, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(ordering=ordering)
        return JsonResponse({"message": "✅ Orden de calibración actualizado", "ok": True})
    except Exception as e:
        print(f"❌ update_calibration_order exception: {e}")
        return JsonResponse({"message": "❌ Error al actualizar orden", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_calibrations_table_info(request: HttpRequest):
    try:
        # Provide table/field metadata via ORM
        fields = [f.name for f in Calibration._meta.get_fields()]
        return JsonResponse({"message": "✅ Información de tabla obtenida", "table": Calibration._meta.db_table, "fields": fields})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener información de tabla", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
@sensitive_endpoint
def update_calibration_table(request: HttpRequest):
    try:
        # Schema management is handled by migrations in Django; keep as no-op
        return JsonResponse({"message": "✅ Operación completada", "ok": True, "note": "Schema managed by Django migrations"})
    except Exception as e:
        return JsonResponse({"message": "❌ Error en operación", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST", "DELETE"])
@jwt_required
@log_api_access
@sensitive_endpoint
def delete_all_calibrations(request: HttpRequest):
    """
    Deletes ALL calibrations for the current factory.
    If the table becomes globally empty, resets the ID sequence.
    """
    try:
        factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
        
        with transaction.atomic():
            # 1. Get all calibration names for this factory to clean up process_code_data
            calibrations = Calibration.objects.filter(factory_id=factory_id)
            names = list(calibrations.values_list('name', flat=True))
            ids = list(calibrations.values_list('id', flat=True))
            
            # 2. Update historic_reports to set calibration_id to NULL
            HistoricReport.objects.filter(calibration_fk__in=ids).update(calibration_fk=None)
            
            # 3. Delete from process_code_data
            ProcessCodeData.objects.filter(process__in=names, factory_id=factory_id).delete()
            
            # 4. Delete calibrations
            count, _ = calibrations.delete()
            
            # 5. Check if table is globally empty to reset sequence
            if not Calibration.objects.exists():
                from django.db import connection
                with connection.cursor() as cursor:
                    # PostgreSQL specific sequence reset
                    cursor.execute("ALTER SEQUENCE crystals_app_calibration_id_seq RESTART WITH 1;")
                    print("✅ Calibration ID sequence reset to 1")

        return JsonResponse({"message": f"✅ Se eliminaron {count} calibraciones", "deleted_count": count})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al eliminar todas las calibraciones", "error": str(e)}, status=500)
