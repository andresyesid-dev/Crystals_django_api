from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..models import AnalysisResults
import json


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def add_analysis_results(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        
        # Create object with all fields from request
        # Since id is auto-assigned, we don't include it
        obj = AnalysisResults.objects.create(
            mean=body.get("mean") or 0.0,
            cv=body.get("cv") or 0.0,
            pct_fine=body.get("pct_fine") or 0.0,
            pct_small=body.get("pct_small") or 0.0,
            pct_optimal=body.get("pct_optimal") or 0.0,
            pct_large=body.get("pct_large") or 0.0,
            pct_very_large=body.get("pct_very_large") or 0.0,
            ratio_l_to_w=body.get("ratio_l_to_w") or 0.0,
            elongated_crystals=body.get("elongated_crystals") or 0.0,
            pct_powder=body.get("pct_powder") or 0.0,
            historic_report_id=body.get("historic_report_id") or 0,
            factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)
        )
        
        return JsonResponse({"message": "✅ Resultados de análisis agregados", "ok": True, "id": obj.id})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al agregar resultados de análisis", "error": str(e)}, status=500)
