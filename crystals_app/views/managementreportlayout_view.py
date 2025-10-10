from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from ..models import ManagementReportLayout
import json


@require_http_methods(["GET"])
@jwt_required
@permission_required('read')
@log_api_access
def get_management_report_layout(request: HttpRequest):
    data = [model_to_dict(o) for o in ManagementReportLayout.objects.all()]
    return JsonResponse({"results": data})


@require_http_methods(["GET"])
@jwt_required
@permission_required('read')
@log_api_access
def get_tab_management_report_layout(request: HttpRequest):
    element_id = request.GET.get("element_id")
    obj = ManagementReportLayout.objects.filter(element_id=element_id).first()
    return JsonResponse({"screen_number": obj.screen_number if obj else None})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def insert_management_report_layout(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    default_data = body.get("default_data") or []
    for item in default_data:
        screen_number, row, column, element_id, element_type = item
        exists = ManagementReportLayout.objects.filter(element_id=element_id).exists()
        if not exists:
            ManagementReportLayout.objects.create(
                screen_number=screen_number,
                row=row,
                column=column,
                element_id=element_id,
                element_type=element_type,
            )
        else:
            ManagementReportLayout.objects.filter(element_id=element_id).update(
                screen_number=screen_number,
                row=row,
                column=column,
                element_type=element_type,
            )
    return JsonResponse({"ok": True})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def update_management_report_layout(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    new_data = body.get("new_data") or []
    for screen_number, row, column, element_id in new_data:
        ManagementReportLayout.objects.filter(element_id=element_id).update(
            screen_number=screen_number, row=row, column=column
        )
    return JsonResponse({"ok": True})


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('write')
@sensitive_endpoint
@log_api_access
def set_default_management_report_layout(request: HttpRequest):
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
        exists = ManagementReportLayout.objects.filter(element_id=element_id).exists()
        if not exists:
            ManagementReportLayout.objects.create(
                screen_number=screen_number,
                row=row,
                column=column,
                element_id=element_id,
                element_type=element_type,
            )
    return JsonResponse({"ok": True})
