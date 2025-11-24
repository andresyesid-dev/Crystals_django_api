from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from django.db.models import Q
from datetime import datetime, timedelta
from ..models import HistoricReport, Calibration, AnalysisCategory
import json


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
        cal = Calibration.objects.filter(name=calibration_name).first()
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
        )
        return JsonResponse({"message": "✅ Reporte histórico agregado", "created": model_to_dict(obj)})
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
        qs = HistoricReport.objects.filter(datetime__gte=start, datetime__lte=end)
        results = []
        cats = {a.historic_report_id: a for a in AnalysisCategory.objects.filter(historic_report_id__in=list(qs.values_list('id', flat=True)))}
        for hr in qs.order_by("datetime"):
            row = model_to_dict(hr)
            ac = cats.get(hr.id)
            if ac:
                row.update({
                    "batch_number": ac.batch_number,
                    "username": ac.username,
                    "baking_time": ac.baking_time,
                    "mass_number": ac.mass_number,
                })
            results.append(row)
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
        qs = HistoricReport.objects.filter(datetime__gte=start, datetime__lte=end, calibration=process)
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
            calibration_fk__ordering__isnull=False
        ).select_related('calibration_fk').order_by("-datetime").first()
        return JsonResponse({"message": "✅ Último reporte obtenido", "result": model_to_dict(obj) if obj else None})
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
        # Match local: SELECT ordering FROM calibrations INNER JOIN historic_reports
        # WHERE historic_reports.calibration_id = :last_calibration
        obj = HistoricReport.objects.filter(
            calibration_fk_id=last_id
        ).select_related('calibration_fk').order_by("-datetime").first()
        
        ordering = obj.calibration_fk.ordering if obj and obj.calibration_fk else None
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
        
        deleted, _ = HistoricReport.objects.filter(id=report_id).delete()
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
        AnalysisCategory.objects.filter(historic_report_id=hr_id).delete()
        from ..models import HistoricAnalysisData
        HistoricAnalysisData.objects.filter(historic_report_id=hr_id).delete()
        HistoricReport.objects.filter(id=hr_id).delete()
        return JsonResponse({"message": "✅ Registro eliminado exitosamente", "deleted": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al eliminar registro", "error": str(e)}, status=500)
