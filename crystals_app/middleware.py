import logging
import time
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from .utils import get_client_ip, log_security_event, SecurityUtils, security_headers_response

security_logger = logging.getLogger('security')


class SecurityMiddleware(MiddlewareMixin):
    """
    Comprehensive security middleware for the Crystals API
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Process incoming requests for security threats
        """
        start_time = time.time()
        request._security_start_time = start_time
        
        # Get client information
        client_ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        # Check for suspicious requests
        is_suspicious, reason = SecurityUtils.is_suspicious_request(request)
        if is_suspicious:
            log_security_event(
                'SUSPICIOUS_REQUEST_BLOCKED',
                request,
                f"Blocked suspicious request: {reason}"
            )
            return JsonResponse({
                'error': 'Request blocked by security policy'
            }, status=403)
        
        # Validate request size
        size_valid, size_reason = SecurityUtils.validate_request_size(request)
        if not size_valid:
            log_security_event(
                'REQUEST_SIZE_VIOLATION',
                request,
                f"Request size violation: {size_reason}"
            )
            return JsonResponse({
                'error': 'Request too large'
            }, status=413)
        
        # Rate limiting per IP
        rate_limit_key = f'rate_limit_{client_ip}'
        request_count = cache.get(rate_limit_key, 0)
        
        # Allow 500 requests per minute per IP (increased for bulk operations like Excel imports)
        if request_count >= 500:
            log_security_event(
                'RATE_LIMIT_EXCEEDED',
                request,
                f"Rate limit exceeded for IP: {client_ip}"
            )
            return JsonResponse({
                'error': 'Rate limit exceeded'
            }, status=429)
        
        cache.set(rate_limit_key, request_count + 1, 60)  # 1 minute window
        
        # Log API access
        if settings.DEBUG:
            security_logger.info(
                f"API Access: {request.method} {request.path}",
                extra={
                    'extra_ip': client_ip,
                    'extra_user': getattr(request.user, 'username', 'Anonymous'),
                    'user_agent': user_agent
                }
            )
        
        return None
    
    def process_response(self, request, response):
        """
        Process outgoing responses
        """
        # Add security headers
        response = security_headers_response(response)
        
        # Log response time and status
        if hasattr(request, '_security_start_time'):
            processing_time = time.time() - request._security_start_time
            
            if processing_time > 5.0:  # Log slow requests
                log_security_event(
                    'SLOW_REQUEST',
                    request,
                    f"Slow request detected: {processing_time:.2f}s"
                )
        
        # Log failed authentication attempts
        if response.status_code == 401:
            log_security_event(
                'UNAUTHORIZED_ACCESS_ATTEMPT',
                request,
                f"Unauthorized access to {request.path}"
            )
        
        # Log server errors
        elif response.status_code >= 500:
            log_security_event(
                'SERVER_ERROR',
                request,
                f"Server error {response.status_code} on {request.path}"
            )
        
        return response
    
    def process_exception(self, request, exception):
        """
        Process exceptions for security logging
        """
        log_security_event(
            'UNHANDLED_EXCEPTION',
            request,
            f"Unhandled exception: {exception.__class__.__name__}: {str(exception)}"
        )
        return None


class IPWhitelistMiddleware(MiddlewareMixin):
    """
    IP Whitelist middleware for production environments
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.whitelist = getattr(settings, 'IP_WHITELIST', [])
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Check if IP is in whitelist (only in production)
        """
        if not settings.DEBUG and self.whitelist:
            client_ip = get_client_ip(request)
            
            if client_ip not in self.whitelist:
                log_security_event(
                    'IP_NOT_WHITELISTED',
                    request,
                    f"Access denied for non-whitelisted IP: {client_ip}"
                )
                return JsonResponse({
                    'error': 'Access denied'
                }, status=403)
        
        return None


class SecurityMonitoringMiddleware(MiddlewareMixin):
    """
    Advanced security monitoring middleware
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Monitor for attack patterns
        """
        client_ip = get_client_ip(request)
        
        # Monitor for brute force attacks
        if request.path in ['/auth/login/', '/user/validate']:
            failed_attempts_key = f'failed_login_{client_ip}'
            failed_attempts = cache.get(failed_attempts_key, 0)
            
            if failed_attempts >= 5:  # Lock after 5 failed attempts
                log_security_event(
                    'BRUTE_FORCE_DETECTED',
                    request,
                    f"Brute force attack detected from IP: {client_ip}"
                )
                return JsonResponse({
                    'error': 'Account temporarily locked due to security concerns'
                }, status=429)
        
        # Monitor for directory traversal attempts
        if '../' in request.path or '..\\' in request.path:
            log_security_event(
                'DIRECTORY_TRAVERSAL_ATTEMPT',
                request,
                f"Directory traversal attempt detected: {request.path}"
            )
            return JsonResponse({
                'error': 'Invalid request'
            }, status=400)
        
        # Monitor for SQL injection patterns
        query_string = request.META.get('QUERY_STRING', '').lower()
        sql_patterns = ['union select', 'or 1=1', 'drop table', 'insert into']
        
        for pattern in sql_patterns:
            if pattern in query_string:
                log_security_event(
                    'SQL_INJECTION_ATTEMPT',
                    request,
                    f"SQL injection attempt detected: {pattern}"
                )
                return JsonResponse({
                    'error': 'Invalid request'
                }, status=400)
        
        return None
    
    def process_response(self, request, response):
        """
        Monitor response patterns
        """
        # Track failed login attempts
        if (request.path in ['/auth/login/', '/user/validate'] and 
            response.status_code in [401, 403]):
            
            client_ip = get_client_ip(request)
            failed_attempts_key = f'failed_login_{client_ip}'
            failed_attempts = cache.get(failed_attempts_key, 0)
            cache.set(failed_attempts_key, failed_attempts + 1, 3600)  # 1 hour
        
        # Clear failed attempts on successful login
        elif (request.path in ['/auth/login/', '/user/validate'] and 
              response.status_code == 200):
            
            client_ip = get_client_ip(request)
            failed_attempts_key = f'failed_login_{client_ip}'
            cache.delete(failed_attempts_key)
        
        return response