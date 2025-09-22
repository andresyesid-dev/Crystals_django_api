from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from datetime import timedelta
from ..models import HistoricAnalysisData, HistoricReport
import json


@csrf_exempt
@require_http_methods(["POST"])
def add_historic_analysis_data(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    hr_id = body.get("historic_reports_id")
    if not hr_id:
        return JsonResponse({"error": "historic_reports_id required"}, status=400)
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
    )
    return JsonResponse({"created": model_to_dict(obj)})


@require_http_methods(["GET"])
def get_analysis_historic_data(request: HttpRequest):
    start = request.GET.get("start")
    end = request.GET.get("end")
    if not start or not end:
        return JsonResponse({"error": "start and end required"}, status=400)
    qs = HistoricAnalysisData.objects.filter(historic_report__datetime__gte=start, historic_report__datetime__lte=end)
    data = [model_to_dict(o) for o in qs]
    return JsonResponse({"results": data})
