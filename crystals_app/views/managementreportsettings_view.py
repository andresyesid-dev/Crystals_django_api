from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import ManagementReportSettings
import json


@require_http_methods(["GET"])
@jwt_required
@sensitive_endpoint
@log_api_access
def get_management_report_settings(request: HttpRequest):
    try:
        obj = ManagementReportSettings.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).first()
        return JsonResponse({"message": "✅ Configuración de reporte de gestión obtenida exitosamente", "result": model_to_dict(obj) if obj else None})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener configuración de reporte", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def insert_management_report_settings(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        obj = ManagementReportSettings.objects.create(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1), **body)
        return JsonResponse({"message": "✅ Configuración de reporte insertada exitosamente", "created": model_to_dict(obj)})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al insertar configuración de reporte", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST", "PATCH"])
@jwt_required
@sensitive_endpoint
@log_api_access
def update_management_report_settings(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        m_r_id = body.get("id")
        if not m_r_id:
            return JsonResponse({"message": "❌ El campo 'id' es requerido", "error": "id required"}, status=400)
        try:
            obj = ManagementReportSettings.objects.get(id=m_r_id, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1))
        except ManagementReportSettings.DoesNotExist:
            return JsonResponse({"message": "❌ Configuración no encontrada", "error": "not found"}, status=404)
        for k, v in body.items():
            if k != "id":
                setattr(obj, k, v)
        obj.save()
        return JsonResponse({"message": "✅ Configuración de reporte actualizada exitosamente", "updated": model_to_dict(obj)})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar configuración de reporte", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def insert_default_management_report_settings(request: HttpRequest):
    """
    Inserts default management report settings if none exist.
    All boolean fields default to 1 (enabled/checked).
    """
    try:
        # Check if settings already exist
        if ManagementReportSettings.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).exists():
            obj = ManagementReportSettings.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).first()
            return JsonResponse({
                "message": "⚠️ Configuración ya existe",
                "result": model_to_dict(obj)
            })
        
        # Create default settings with all fields set to 1 (enabled)
        default_settings = ManagementReportSettings.objects.create(
            mean_variable=1,
            cv_variable=1,
            perc_fino=1,
            perc_peq=1,
            perc_opt=1,
            perc_gran=1,
            perc_muygran=1,
            rel_la=1,
            perc_crst_alarg=1,
            pza_licor=1,
            pza_sirope=1,
            pza_masa_refino=1,
            pza_magma_b=1,
            pza_meladura=1,
            pza_masa_a=1,
            pza_lavado_a=1,
            pza_nutsch_a=1,
            pza_magma_c=1,
            pza_miel_a=1,
            pza_masa_b=1,
            pza_nutsch_b=1,
            pza_cr_des=1,
            pza_miel_b=1,
            pza_masa_c=1,
            pza_nutsch_c=1,
            pza_miel_final=1,
            bx_masa_c=1,
            bx_cristal_des=1,
            bx_nutsch_c=1,
            bx_masa_b=1,
            bx_masa_a=1,
            bx_magma_b=1,
            bx_masa_refino=1,
            bx_magma_c=1,
            bx_miel_final=1,
            bx_nutsch_b=1,
            bx_miel_b=1,
            bx_miel_a=1,
            bx_lavado_a=1,
            bx_nutsch_a=1,
            bx_sirope=1,
            bx_del_licor=1,
            bx_meladura=1,
            pol_azuc=1,
            sol_tota_hda_azu=1,
            rel_la_grapgh=1,
            amount_perc_fino=0,
            amount_perc_peq=0,
            amount_perc_opt=0,
            amount_perc_gran=0,
            amount_perc_muy_gran=0,
            amount_total=0,
            perc_powder=0,
            factory_id=request.factory_id
        )
        
        return JsonResponse({
            "message": "✅ Configuración por defecto creada exitosamente",
            "created": model_to_dict(default_settings)
        }, status=201)
        
    except Exception as e:
        import traceback
        return JsonResponse({
            "message": "❌ Error al crear configuración por defecto",
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status=500)
