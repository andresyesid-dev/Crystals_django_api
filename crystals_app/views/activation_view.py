from django.http import JsonResponse, HttpRequest
from ..decorators import jwt_required, permission_required, log_api_access, sensitive_endpoint
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from ..models import Activation
import json


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('read')
@log_api_access
def validate_software(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    given_code = body.get("code")
    if not given_code:
        return JsonResponse({"ok": False, "error": "code required"}, status=400)
    act = Activation.objects.filter(id=1).first()
    if not act:
        return JsonResponse({"ok": False})
    valid = False
    try:
        from pbkdf2 import crypt as pbkdf2_crypt  # type: ignore
        try:
            valid = pbkdf2_crypt(given_code, act.validation_code) == act.validation_code
        except Exception:
            valid = False
    except Exception:
        valid = False
    valid = valid or (given_code == act.validation_code)
    if valid:
        act.validated = 1
        act.save()
        return JsonResponse({"ok": True})
    return JsonResponse({"ok": False})


@require_http_methods(["GET"])
@jwt_required
@permission_required('read')
@log_api_access
def check_if_software_is_active(request: HttpRequest):
    act = Activation.objects.filter(id=1).first()
    return JsonResponse({"active": bool(act and int(act.validated) == 1)})
