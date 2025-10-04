from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from ..models import User
from ..decorators import rate_limit_protected, log_api_access
import json


@require_http_methods(["POST"])
@rate_limit_protected(rate='5/m')  # Limit login attempts
@log_api_access
def validate_user_credentials(request: HttpRequest):
    body = json.loads(request.body or b"{}")
    username = body.get("username")
    password = body.get("password")
    if not username or password is None:
        return JsonResponse({"ok": False, "error": "username and password required"}, status=400)
    u = User.objects.filter(username=username).first()
    if not u:
        return JsonResponse({"ok": False})
    return JsonResponse({"ok": u.password == password})
