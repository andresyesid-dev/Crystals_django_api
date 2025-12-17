from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..models import AnalysisCategory, NewParametersAnalysisCategory, SpecificReportingOrder, CrystalsDataParametrizationNewParams
import json


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def add_analysis_cat_values(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        hr_id = body.get("historic_reports_id")
        values = body.get("values") or []
        if not hr_id:
            return JsonResponse({"message": "❌ ID de reporte requerido", "error": "historic_reports_id required"}, status=400)
        data = {k: (v if v != "" else None) for k, v in values}
        data["historic_report_id"] = hr_id
        data["factory_id"] = request.META.get('HTTP_X_FACTORY_ID', 1)
        AnalysisCategory.objects.create(**data)
        return JsonResponse({"message": "✅ Valores agregados exitosamente", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al agregar valores", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def add_new_parameters_analysis_categories(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        parameter = (body.get("parameter") or "").replace(' ', '_')
        type_ = body.get("type")
        if not parameter or not type_:
            return JsonResponse({"message": "❌ Parámetro y tipo requeridos", "error": "parameter and type required"}, status=400)
            
        # Create or Get the parameter definition
        # We continue execution even if it exists to ensure side-effects (columns/params) are applied logic
        _, created = NewParametersAnalysisCategory.objects.get_or_create(
            parameter=parameter, 
            factory_id=request.META.get('HTTP_X_FACTORY_ID', 1),
            defaults={'type': type_}
        )
        
        # Execute raw SQL to add column to analysis_categories table (Requested by user)
        # Note: This schema change affects the table globally in the shared DB schema.
        from django.db import connection
        sql_type = "TEXT" if type_ == "Text" else "DOUBLE PRECISION"
        with connection.cursor() as cursor:
            # Postgres supports IF NOT EXISTS for ADD COLUMN in newer versions.
            # We use it to prevent errors if the column was added manually or by another factory (shared schema).
            cursor.execute(f"ALTER TABLE analysis_categories ADD COLUMN IF NOT EXISTS {parameter} {sql_type}")
            
        # Create default parametrization entries (Good, Regular, Bad ranges)
        # Required for the client to process/color the column values without crashing.
        for category in ["Good", "Regular", "Bad"]:
             CrystalsDataParametrizationNewParams.objects.get_or_create(
                 parameter=parameter, 
                 categoria=category, 
                 factory_id=request.META.get('HTTP_X_FACTORY_ID', 1),
                 defaults={'range_from': 0, 'range_to': 0}
             )

        message = "✅ Parámetro agregado exitosamente" if created else "⚠️ El parámetro ya existe (Se verificaron columnas y configuración)"
        return JsonResponse({"message": message, "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al agregar parámetro", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_new_parameters_analysis_categories(request: HttpRequest):
    try:
        data = list(NewParametersAnalysisCategory.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).values())
        return JsonResponse({"message": "✅ Parámetros obtenidos", "results": data})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener parámetros", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def delete_parameter_analysis_category(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        parameter = (body.get("parameter") or "").replace(' ', '_')
        if not parameter:
            return JsonResponse({"message": "❌ Parámetro requerido", "error": "parameter required"}, status=400)
        NewParametersAnalysisCategory.objects.filter(parameter=parameter, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).delete()
        SpecificReportingOrder.objects.filter(value=parameter.replace('_', ' '), factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).delete()
        return JsonResponse({"message": "✅ Parámetro eliminado exitosamente", "deleted": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al eliminar parámetro", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def check_category_exists(request: HttpRequest):
    try:
        parameter = request.GET.get("parameter")
        if not parameter:
            return JsonResponse({"message": "❌ Parámetro requerido", "error": "parameter required"}, status=400)
        
        parameter = parameter.replace(' ', '_')
        exists = NewParametersAnalysisCategory.objects.filter(parameter=parameter, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).exists()
        return JsonResponse({"message": "✅ Verificación completada", "exists": exists})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al verificar parámetro", "error": str(e)}, status=500)
