from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from django.db.models import Q
from datetime import datetime, timedelta
from ..models import HistoricReport, Calibration, AnalysisCategory
import json


# Orden POSICIONAL canónico de la tabla SQLite local `historic_reports`
# (ver crystals3.0/src/database/schema/tables.sql). El cliente accede a este
# registro por índice numérico (last_report.value(16) == height_cv,
# value(17) == height_mean en analysis_graphs_widget.py), así que el dict que
# devolvemos DEBE preservar exactamente este orden — los dicts de Python
# conservan orden de inserción y el cliente lo lee posicionalmente.
#
# Diferencia clave con model_to_dict(): SQLite tiene `id` en 0 y `calibration_id`
# en 2 (columna que el modelo Django llama calibration_fk y coloca al final).
# Sin este orden, value(16) cae sobre height_mean/height_sum y, peor, sobre los
# campos nullable height_median/height_skewness que pueden ser None -> el cliente
# revienta con "conversion from NoneType to Decimal is not supported".
#
# Los campos median/skewness (nullable en el modelo) se emiten con fallback 0.0
# para blindar el acceso posicional del cliente aunque en BD sean NULL.
def _serialize_historic_report_sqlite_order(hr):
    def num(v):
        return v if v is not None else 0.0
    return {
        "id": hr.id,
        "datetime": hr.datetime,
        "calibration_id": hr.calibration_fk_id,
        "calibration": hr.calibration,
        "correlation": num(hr.correlation),
        "width_min": num(hr.width_min),
        "width_max": num(hr.width_max),
        "width_sd": num(hr.width_sd),
        "width_cv": num(hr.width_cv),
        "width_mean": num(hr.width_mean),
        "width_sum": num(hr.width_sum),
        "width_samples": num(hr.width_samples),
        "width_range": num(hr.width_range),
        "height_min": num(hr.height_min),
        "height_max": num(hr.height_max),
        "height_sd": num(hr.height_sd),
        "height_cv": num(hr.height_cv),        # índice 16
        "height_mean": num(hr.height_mean),    # índice 17
        "height_sum": num(hr.height_sum),
        "height_samples": num(hr.height_samples),
        "height_range": num(hr.height_range),
        # Campos añadidos después (migración 0014). Van al final para NO
        # desplazar los índices 0-19 que el cliente lee posicionalmente. Se
        # exponen por nombre para que el cliente pueda migrar a acceso canónico.
        "height_median": num(hr.height_median),
        "height_skewness": num(hr.height_skewness),
        "width_median": num(hr.width_median),
        "width_skewness": num(hr.width_skewness),
        "factory_id": hr.factory_id,
    }


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def add_historic_report(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        analysis_datetime = body.get("datetime")
        calibration_name = body.get("calibration")
        metrics = body.get("metrics") or {}
        if not calibration_name or not analysis_datetime or not metrics:
            return JsonResponse({"message": "❌ Los campos 'datetime', 'calibration' y 'metrics' son requeridos", "error": "datetime, calibration and metrics required"}, status=400)
        cal = Calibration.objects.filter(name=calibration_name, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).first()
        if not cal:
            return JsonResponse({"message": "❌ Calibración no encontrada", "error": "Calibration not found"}, status=404)
        common = metrics.get("common", {})
        width = metrics.get("width", {})
        height = metrics.get("height", {})
        obj = HistoricReport.objects.create(
            datetime=analysis_datetime,
            calibration=cal.name,
            calibration_fk=cal,
            correlation=float(common.get("correlation", [0])[0]) if common.get("correlation") else 0.0,
            width_min=float(width.get("min", 0) or 0),
            width_max=float(width.get("max", 0) or 0),
            width_sd=float(width.get("sd", 0) or 0),
            width_cv=float(width.get("cv", 0) or 0),
            width_mean=float(width.get("mean", 0) or 0),
            width_sum=float(width.get("sum", 0) or 0),
            width_samples=float(width.get("samples", 0) or 0),
            width_range=float(width.get("range", 0) or 0),
            height_min=float(height.get("min", 0) or 0),
            height_max=float(height.get("max", 0) or 0),
            height_sd=float(height.get("sd", 0) or 0),
            height_cv=float(height.get("cv", 0) or 0),
            height_mean=float(height.get("mean", 0) or 0),
            height_sum=float(height.get("sum", 0) or 0),
            height_samples=float(height.get("samples", 0) or 0),
            height_range=float(height.get("range", 0) or 0),
            height_median=float(height.get("median", 0) or 0),
            height_skewness=float(height.get("skewness", 0) or 0),
            width_median=float(width.get("median", 0) or 0),
            width_skewness=float(width.get("skewness", 0) or 0),
            factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)
        )
        return JsonResponse({"message": "✅ Reporte histórico agregado", "id": obj.id})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al agregar reporte", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_historic_reports(request: HttpRequest):
    try:
        start = request.GET.get("start")
        end = request.GET.get("end")
        additional = request.GET.getlist("cols")
        if not start or not end:
            return JsonResponse({"message": "❌ Los parámetros 'start' y 'end' son requeridos", "error": "start and end required (YYYY-mm-dd HH:MM:SS)"}, status=400)
        qs = HistoricReport.objects.filter(datetime__gte=start, datetime__lte=end, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1))
        results = []
        cats = {a.historic_report_id: a for a in AnalysisCategory.objects.filter(historic_report_id__in=list(qs.values_list('id', flat=True)), factory_id=request.META.get('HTTP_X_FACTORY_ID', 1))}
        
        for hr in qs:
            try:
                # Orden posicional idéntico a SQLite (id, datetime, calibration_id,
                # ...) para que el acceso por índice del cliente sea correcto.
                # Las columnas del LEFT JOIN (AnalysisCategory) se agregan después,
                # igual que antes.
                row = _serialize_historic_report_sqlite_order(hr)

                # Mimic LEFT JOIN behavior: Ensure keys exist even if AnalysisCategory is missing
                ac = cats.get(hr.id)
                if ac:
                    row.update({
                        "batch_number": ac.batch_number,
                        "username": ac.username,
                        "baking_time": ac.baking_time,
                        "mass_number": ac.mass_number,
                    })
                else:
                    row.update({
                        "batch_number": None,
                        "username": None,
                        "baking_time": None,
                        "mass_number": None,
                    })
                
                results.append(row)
            except Exception as row_error:
                continue

        return JsonResponse({"message": "✅ Reportes históricos obtenidos", "results": results})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener reportes", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_historic_reports_for_process(request: HttpRequest):
    try:
        start = request.GET.get("start")
        end = request.GET.get("end")
        process = request.GET.get("process")
        if not all([start, end, process]):
            return JsonResponse({"message": "❌ Los parámetros 'start', 'end' y 'process' son requeridos", "error": "start, end, process required"}, status=400)
        qs = HistoricReport.objects.filter(datetime__gte=start, datetime__lte=end, calibration=process, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1))
        return JsonResponse({"message": "✅ Reportes por proceso obtenidos", "results": [model_to_dict(o) for o in qs.order_by("datetime")]})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener reportes", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_last_report(request: HttpRequest):
    try:
        start = request.GET.get("start")
        end = request.GET.get("end")
        if not start or not end:
            return JsonResponse({"message": "❌ Los parámetros 'start' y 'end' son requeridos", "error": "start and end required"}, status=400)
        # Match local: INNER JOIN with calibrations WHERE ordering is not null
        obj = HistoricReport.objects.filter(
            datetime__gte=start,
            datetime__lte=end,
            calibration_fk__ordering__isnull=False,
            factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)
        ).select_related('calibration_fk').order_by("-datetime").first()
        result = None
        if obj:
            # Orden posicional idéntico a SQLite: el cliente lee
            # last_report.value(16)/value(17) por índice (height_cv/height_mean).
            result = _serialize_historic_report_sqlite_order(obj)
        return JsonResponse({"message": "✅ Último reporte obtenido", "result": result})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener último reporte", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_order_last_report(request: HttpRequest):
    try:
        last_id = request.GET.get("last_id")
        if not last_id:
            return JsonResponse({"message": "❌ El parámetro 'last_id' es requerido", "error": "last_id required"}, status=400)
        # Contrato canónico (SQLite): SELECT ordering FROM calibrations
        # WHERE calibrations.id = :last_calibration. El cliente envía el ID
        # numérico de la calibración (confirmado contra historic_reports.py:129
        # y historic_reports_table.py:185, que filtran por calibration_id).
        # Se mantiene fallback por nombre por compatibilidad con flujos antiguos
        # que pudieran enviar el nombre en vez del id.
        factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
        calibration = None
        if str(last_id).isdigit():
            calibration = Calibration.objects.filter(
                id=int(last_id), factory_id=factory_id
            ).first()
        if calibration is None:
            calibration = Calibration.objects.filter(
                name=last_id, factory_id=factory_id
            ).first()

        ordering = calibration.ordering if calibration else None
        return JsonResponse({"message": "✅ Orden obtenido", "ordering": ordering})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener orden", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def delete_last_report_db(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        # Match local: receives last_report object, extracts id from value(0)
        last_report = body.get("last_report")
        if not last_report:
            return JsonResponse({"message": "❌ El campo 'last_report' es requerido", "error": "last_report dict required with id key"}, status=400)
        
        # Extract id - local uses last_report.value(0) which is the first column (id)
        report_id = last_report.get("id") if isinstance(last_report, dict) else last_report
        
        deleted, _ = HistoricReport.objects.filter(id=report_id, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).delete()
        return JsonResponse({"message": "✅ Reporte eliminado exitosamente", "deleted": bool(deleted)})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al eliminar reporte", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def delete_management_record(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        hr_id = body.get("hr_id")
        if not hr_id:
            return JsonResponse({"message": "❌ El campo 'hr_id' es requerido", "error": "hr_id required"}, status=400)
        AnalysisCategory.objects.filter(historic_report_id=hr_id, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).delete()
        from ..models import HistoricAnalysisData
        HistoricAnalysisData.objects.filter(historic_report_id=hr_id, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).delete()
        HistoricReport.objects.filter(id=hr_id, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).delete()
        return JsonResponse({"message": "✅ Registro eliminado exitosamente", "deleted": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al eliminar registro", "error": str(e)}, status=500)
