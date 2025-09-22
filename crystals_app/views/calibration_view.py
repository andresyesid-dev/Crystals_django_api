from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict
from django.db import transaction
from ..models import Calibration
import json


def _parse_json(request: HttpRequest):
    try:
        return json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        return {}


@require_http_methods(["GET"])
def select_calibrations(request: HttpRequest):
    qs = Calibration.objects.all().order_by("-active", "name")
    data = [model_to_dict(o) for o in qs]
    return JsonResponse({"results": data})


@require_http_methods(["GET"])
def select_historic_reports_calibrations(request: HttpRequest):
    # In original code, filtered by ordering not null. Here we list all.
    data = [model_to_dict(o) for o in Calibration.objects.all().order_by("name")]
    return JsonResponse({"results": data})


@require_http_methods(["GET"])
def select_excluded_reports_calibrations(request: HttpRequest):
    # In original, those without ordering. Not available in ORM model; return empty list for compatibility.
    return JsonResponse({"results": []})


@require_http_methods(["GET"])
def select_active_calibration(request: HttpRequest):
    c = Calibration.objects.filter(active=1).first()
    return JsonResponse({"result": model_to_dict(c) if c else None})


@csrf_exempt
@require_http_methods(["POST"])
def set_calibration_as_active(request: HttpRequest):
    payload = _parse_json(request)
    name = payload.get("name")
    if not name:
        return JsonResponse({"error": "name is required"}, status=400)
    with transaction.atomic():
        Calibration.objects.update(active=0)
        Calibration.objects.filter(name=name).update(active=1)
    return JsonResponse({"ok": True})


@csrf_exempt
@require_http_methods(["POST"])
def create_calibration(request: HttpRequest):
    payload = _parse_json(request)
    fields = {k: v for k, v in payload.items() if k in {"name", "pixels_per_metric", "metric_name", "range", "active", "powder"}}
    obj = Calibration.objects.create(**fields)
    return JsonResponse({"created": model_to_dict(obj)}, status=201)


@csrf_exempt
@require_http_methods(["POST", "PATCH"])
def update_calibration(request: HttpRequest):
    payload = _parse_json(request)
    calibration_id = payload.get("id")
    if not calibration_id:
        return JsonResponse({"error": "id is required"}, status=400)
    try:
        obj = Calibration.objects.get(id=calibration_id)
    except Calibration.DoesNotExist:
        return JsonResponse({"error": "Calibration not found"}, status=404)
    updatable = {"name", "pixels_per_metric", "metric_name", "range", "active", "powder"}
    for k in updatable:
        if k in payload:
            setattr(obj, k, payload[k])
    obj.save()
    return JsonResponse({"updated": model_to_dict(obj)})


@csrf_exempt
@require_http_methods(["POST"])
def delete_calibration(request: HttpRequest):
    payload = _parse_json(request)
    calibration_id = payload.get("id")
    if not calibration_id:
        return JsonResponse({"error": "id is required"}, status=400)
    deleted, _ = Calibration.objects.filter(id=calibration_id).delete()
    return JsonResponse({"deleted": bool(deleted)})


@require_http_methods(["GET"])
def get_calibration(request: HttpRequest):
    name = request.GET.get("name")
    if not name:
        return JsonResponse({"error": "name is required"}, status=400)
    obj = Calibration.objects.filter(name=name).first()
    return JsonResponse({"result": model_to_dict(obj) if obj else None})


@csrf_exempt
@require_http_methods(["POST"])
def update_calibration_order(request: HttpRequest):
    # Field 'ordering' not present in ORM model; keep no-op for compatibility
    return JsonResponse({"ok": True, "note": "ordering field not available; no-op"})


@require_http_methods(["GET"])
def get_calibrations_table_info(request: HttpRequest):
    # Provide table/field metadata via ORM
    fields = [f.name for f in Calibration._meta.get_fields()]
    return JsonResponse({"table": Calibration._meta.db_table, "fields": fields})


@require_http_methods(["GET"])
def update_calibration_table(request: HttpRequest):
    # Schema management is handled by migrations in Django; keep as no-op
    return JsonResponse({"ok": True, "note": "Schema managed by Django migrations"})
