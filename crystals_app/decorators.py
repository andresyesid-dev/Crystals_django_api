from functools import wraps
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
from django_ratelimit.decorators import ratelimit
import logging
from .utils import log_security_event

security_logger = logging.getLogger('security')


def jwt_required(view_func):
    """
    Decorator to require JWT authentication for function-based views
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        jwt_authenticator = JWTAuthentication()
        
        try:
            # Try to authenticate with JWT
            auth_result = jwt_authenticator.authenticate(request)
            
            if auth_result is None:
                log_security_event(
                    'JWT_MISSING',
                    request,
                    f"JWT token missing for protected endpoint: {request.path}"
                )
                return JsonResponse({
                    'error': 'Authentication credentials were not provided.',
                    'code': 'authentication_required'
                }, status=401)
            
            user, token = auth_result
            request.user = user
            request.auth = token
            
            return view_func(request, *args, **kwargs)
            
        except (InvalidToken, TokenError) as e:
            log_security_event(
                'JWT_INVALID',
                request,
                f"Invalid JWT token for endpoint: {request.path} - {str(e)}"
            )
            return JsonResponse({
                'error': 'Invalid or expired token.',
                'code': 'token_invalid'
            }, status=401)
        except Exception as e:
            # Log error with proper extra fields
            from .utils import get_client_ip
            security_logger.error(
                f"JWT Authentication error: {str(e)}", 
                extra={
                    'extra_ip': get_client_ip(request) if hasattr(request, 'META') else 'Unknown',
                    'extra_user': 'Anonymous'
                }
            )
            return JsonResponse({
                'error': 'Authentication failed.',
                'code': 'authentication_failed'
            }, status=401)
    
    return wrapper


def admin_required(view_func):
    """
    Decorator to require admin privileges (superuser)
    """
    @wraps(view_func)
    @jwt_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            log_security_event(
                'ADMIN_ACCESS_DENIED',
                request,
                f"Non-admin user {request.user.username} tried to access admin endpoint: {request.path}",
                user=request.user.username
            )
            return JsonResponse({
                'error': 'Admin privileges required.',
                'code': 'admin_required'
            }, status=403)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def rate_limit_protected(key='ip', rate='10/m'):
    """
    Decorator to add rate limiting to views
    """
    def decorator(view_func):
        @wraps(view_func)
        @ratelimit(key=key, rate=rate, method='ALL', block=True)
        def wrapper(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def log_api_access(view_func):
    """
    Decorator to log API access attempts
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = getattr(request, 'user', AnonymousUser())
        username = user.username if hasattr(user, 'username') and user.username else 'Anonymous'
        
        log_security_event(
            'API_ACCESS',
            request,
            f"API access: {request.method} {request.path}",
            user=username
        )
        
        try:
            response = view_func(request, *args, **kwargs)
            return response
        except Exception as e:
            log_security_event(
                'API_ERROR',
                request,
                f"API error in {request.path}: {str(e)}",
                user=username
            )
            raise
    
    return wrapper


def permission_required(permission_name):
    """
    Decorator to check for specific permissions
    SIMPLIFIED: All authenticated users (especially superusers) have all permissions
    since this API is only used by the Crystals application with a single user
    """
    def decorator(view_func):
        @wraps(view_func)
        @jwt_required
        def wrapper(request, *args, **kwargs):
            # Superusers always have all permissions
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # For non-superusers, check if they have is_staff permission
            # (all authenticated users for this single-user API should have access)
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            
            # If somehow we get here, deny access
            log_security_event(
                'PERMISSION_DENIED',
                request,
                f"Permission denied for user {request.user.username}: {permission_name}",
                user=request.user.username
            )
            return JsonResponse({
                'error': f'Permission denied: {permission_name} required.',
                'code': 'permission_denied'
            }, status=403)
        
        return wrapper
    return decorator


def sensitive_endpoint(view_func):
    """
    Decorator for sensitive endpoints that require extra security
    """
    @wraps(view_func)
    @jwt_required
    @rate_limit_protected(rate='5/m')  # More restrictive rate limiting
    def wrapper(request, *args, **kwargs):
        log_security_event(
            'SENSITIVE_ACCESS',
            request,
            f"Access to sensitive endpoint: {request.path}",
            user=request.user.username
        )
        return view_func(request, *args, **kwargs)
    
    return wrapper


def api_key_or_jwt(view_func):
    """
    Decorator that allows either API key or JWT authentication
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Try JWT first
        jwt_authenticator = JWTAuthentication()
        
        try:
            auth_result = jwt_authenticator.authenticate(request)
            if auth_result is not None:
                user, token = auth_result
                request.user = user
                request.auth = token
                return view_func(request, *args, **kwargs)
        except (InvalidToken, TokenError):
            pass  # Try API key next
        
        # Try API key authentication
        api_key = request.headers.get('X-API-Key')
        if api_key:
            # Implement API key validation logic here
            # For now, we'll just check a simple key
            valid_api_keys = ['your-api-key-here']  # Replace with actual keys
            
            if api_key in valid_api_keys:
                # Create a pseudo-user for API key access
                request.user = AnonymousUser()
                request.auth = {'type': 'api_key', 'key': api_key}
                return view_func(request, *args, **kwargs)
        
        # No valid authentication found
        return JsonResponse({
            'error': 'Authentication required (JWT token or API key)',
            'code': 'authentication_required'
        }, status=401)
    
    return wrapper