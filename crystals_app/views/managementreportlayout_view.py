from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import ManagementReportLayout
import json


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_management_report_layout(request: HttpRequest):
    try:
        factory_id = request.META.get('HTTP_X_FACTORY_ID', 1)
        qs = ManagementReportLayout.objects.filter(factory_id=factory_id)
        
        # Auto-create defaults if empty (Matching local table logic)
        if not qs.exists():
            default_data = [
                (1, 0, 0, "general_data_table", "table"),
                (1, 0, 1, "mean_line_chart", "graph"),
                (1, 0, 2, "dop_bar_chart", "graph"),
                (1, 1, 0, "specific_data_table", "table"),
                (1, 1, 1, "cv_line_chart", "graph"),
                (2, 0, 0, "general_laboratory_table", "table"),
                (2, 0, 1, "specific_laboratory_table", "table"),
                (2, 0, 2, "calculated_laboratory_data", "table"),
                (2, 1, 0, "fall_of_purity_laboratory_data", "graph"),
                (2, 1, 1, "percentage_of_crystals_per_mass", "graph"),
                (2, 1, 2, "calculated_individual_reports", "table"),
            ]
            layouts = [
                ManagementReportLayout(
                    screen_number=item[0], row=item[1], column=item[2],
                    element_id=item[3], element_type=item[4], factory_id=factory_id
                ) for item in default_data
            ]
            ManagementReportLayout.objects.bulk_create(layouts)
            qs = ManagementReportLayout.objects.filter(factory_id=factory_id)

        data = [model_to_dict(o) for o in qs]
        return JsonResponse({"message": "✅ Diseño de reporte de gestión obtenido exitosamente", "results": data})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener diseño de reporte", "error": str(e)}, status=500)


@require_http_methods(["GET"])
@jwt_required
@log_api_access
def get_tab_management_report_layout(request: HttpRequest):
    try:
        element_id = request.GET.get("element_id")
        obj = ManagementReportLayout.objects.filter(element_id=element_id, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).first()
        return JsonResponse({"message": "✅ Pestaña de diseño obtenida exitosamente", "screen_number": obj.screen_number if obj else None})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al obtener pestaña de diseño", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def insert_management_report_layout(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        default_data = body.get("default_data") or []
        for item in default_data:
            screen_number, row, column, element_id, element_type = item
            exists = ManagementReportLayout.objects.filter(element_id=element_id, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).exists()
            if not exists:
                ManagementReportLayout.objects.create(
                    screen_number=screen_number,
                    row=row,
                    column=column,
                    element_id=element_id,
                    element_type=element_type,
                    factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)
                )
            else:
                ManagementReportLayout.objects.filter(element_id=element_id, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(
                    screen_number=screen_number,
                    row=row,
                    column=column,
                    element_type=element_type,
                )
        return JsonResponse({"message": "✅ Diseño de reporte insertado/actualizado exitosamente", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al insertar diseño de reporte", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST", "PATCH"])
@jwt_required
@sensitive_endpoint
@log_api_access
def update_management_report_layout(request: HttpRequest):
    try:
        body = json.loads(request.body or b"{}")
        new_data = body.get("new_data") or []
        for screen_number, row, column, element_id in new_data:
            ManagementReportLayout.objects.filter(element_id=element_id, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).update(
                screen_number=screen_number, row=row, column=column
            )
        return JsonResponse({"message": "✅ Diseño de reporte actualizado exitosamente", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al actualizar diseño de reporte", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@sensitive_endpoint
@log_api_access
def set_default_management_report_layout(request: HttpRequest):
    try:
        default_data = [
            (1, 0, 0, "general_data_table", "table"),
            (1, 0, 1, "mean_line_chart", "graph"),
            (1, 0, 2, "dop_bar_chart", "graph"),
            (1, 1, 0, "specific_data_table", "table"),
            (1, 1, 1, "cv_line_chart", "graph"),
            (2, 0, 0, "general_laboratory_table", "table"),
            (2, 0, 1, "specific_laboratory_table", "table"),
            (2, 0, 2, "calculated_laboratory_data", "table"),
            (2, 1, 0, "fall_of_purity_laboratory_data", "graph"),
            (2, 1, 1, "percentage_of_crystals_per_mass", "graph"),
            (2, 1, 2, "calculated_individual_reports", "table"),
        ]
        # Reuse insert/update behavior
        for item in default_data:
            screen_number, row, column, element_id, element_type = item
            exists = ManagementReportLayout.objects.filter(element_id=element_id, factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).exists()
            if not exists:
                ManagementReportLayout.objects.create(
                    screen_number=screen_number,
                    row=row,
                    column=column,
                    element_id=element_id,
                    element_type=element_type,
                    factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)
                )
        return JsonResponse({"message": "✅ Diseño predeterminado establecido exitosamente", "ok": True})
    except Exception as e:
        return JsonResponse({"message": "❌ Error al establecer diseño predeterminado", "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@log_api_access
def insert_default_management_report_layout(request: HttpRequest):
    """
    Inserts default management report layout if table is empty.
    Called during initial setup.
    """
    try:
        count = ManagementReportLayout.objects.filter(factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)).count()
        if count > 0:
            return JsonResponse({
                "ok": True,
                "already_exists": True,
                "message": f"⚠️ Ya existen {count} elementos de diseño"
            })
        
        default_data = [
            (1, 0, 0, "general_data_table", "table"),
            (1, 0, 1, "mean_line_chart", "graph"),
            (1, 0, 2, "dop_bar_chart", "graph"),
            (1, 1, 0, "specific_data_table", "table"),
            (1, 1, 1, "cv_line_chart", "graph"),
            (2, 0, 0, "general_laboratory_table", "table"),
            (2, 0, 1, "specific_laboratory_table", "table"),
            (2, 0, 2, "calculated_laboratory_data", "table"),
            (2, 1, 0, "fall_of_purity_laboratory_data", "graph"),
            (2, 1, 1, "percentage_of_crystals_per_mass", "graph"),
            (2, 1, 2, "calculated_individual_reports", "table"),
        ]
        
        layouts = []
        for item in default_data:
            screen_number, row, column, element_id, element_type = item
            layouts.append(ManagementReportLayout(
                screen_number=screen_number,
                row=row,
                column=column,
                element_id=element_id,
                element_type=element_type,
                factory_id=request.META.get('HTTP_X_FACTORY_ID', 1)
            ))
        
        ManagementReportLayout.objects.bulk_create(layouts)
        
        return JsonResponse({
            "ok": True,
            "created": len(layouts),
            "message": f"✅ Se insertaron {len(layouts)} elementos de diseño por defecto"
        })
    except Exception as e:
        return JsonResponse({
            "message": "❌ Error al insertar diseño por defecto",
            "error": str(e)
        }, status=500)
