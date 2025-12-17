from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from datetime import timedelta
from ..models import HistoricAnalysisData, HistoricReport
import json


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def add_historic_analysis_data(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        hr_id = body.get("historic_reports_id")
        if not hr_id:
            return JsonResponse({"message": "❌ El campo 'historic_reports_id' es requerido", "error": "historic_reports_id required"}, status=400)
        obj = HistoricAnalysisData.objects.create(
            historic_report_id=hr_id,
            range_class=body.get("range_class"),
            object_length=body.get("object_length") or 0,
            pct_object_length=body.get("pct_object_length") or 0,
            mean_object_length=body.get("mean_object_length") or 0,
            object_width=body.get("object_width") or 0,
            pct_object_width=body.get("pct_object_width") or 0,
            mean_object_width=body.get("mean_object_width") or 0,
            long_crystals=body.get("long_crystals") or None,
            factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)
        )
        return JsonResponse({"message": "✅ Datos de análisis histórico agregados", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al agregar datos", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_analysis_historic_data(request: HttpRequest):
    try:
        start = request.GET.get("start")
        end = request.GET.get("end")
        if not start or not end:
            return JsonResponse({"message": "❌ Los parámetros 'start' y 'end' son requeridos", "error": "start and end required"}, status=400)
            
        # Use select_related to optimize the join
        qs = HistoricAnalysisData.objects.filter(historic_report__datetime__gte=start, historic_report__datetime__lte=end, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).select_related('historic_report')
        
        results = []
        for analysis in qs:
            row = model_to_dict(analysis)
            hr = analysis.historic_report
            
            # Add joined fields expected by client (matching HistoricAnalysisDataTable local query)
            row.update({
                "hr_id": hr.id,
                "hr_datetime": hr.datetime,
                "calibration": hr.calibration,
                "width_mean": hr.width_mean,
                "height_mean": hr.height_mean,
                "height_cv": hr.height_cv,
                "width_samples": hr.width_samples
            })
            results.append(row)
            
        return JsonResponse({"message": "✅ Datos históricos obtenidos", "results": results})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener datos", "error": str(e)}, status=500)
