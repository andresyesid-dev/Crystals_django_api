import logging
from datetime import datetime
from django.http import JsonResponse
from rest_framework.views import exception_handler
from rest_framework import status

security_logger = logging.getLogger('security')


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """
    Get user agent from request
    """
    return request.META.get('HTTP_USER_AGENT', 'Unknown')


def log_security_event(event_type, request, message, user=None):
    """
    Log security events with structured information
    """
    ip = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    extra_data = {
        'extra_ip': ip,
        'extra_user': user or 'Anonymous',
        'user_agent': user_agent,
        'event_type': event_type,
        'timestamp': datetime.now().isoformat(),
        'path': request.path,
        'method': request.method
    }
    
    security_logger.warning(message, extra=extra_data)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        request = context.get('request')
        if request:
            log_security_event(
                'API_ERROR',
                request,
                f"API Error: {exc.__class__.__name__} - {str(exc)}"
            )
    
    return response


class SecurityUtils:
    """
    Utility class for security-related functions
    """
    
    @staticmethod
    def is_suspicious_request(request):
        """
        Check if request shows suspicious patterns
        """
        suspicious_patterns = [
            'SELECT * FROM',
            'UNION SELECT',
            '<script>',
            'javascript:',
            '../../../',
            'php://input',
        ]
        
        # Check URL and query parameters
        full_path = request.get_full_path().lower()
        for pattern in suspicious_patterns:
            if pattern.lower() in full_path:
                return True, f"Suspicious pattern in URL: {pattern}"
        
        # Check headers
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        suspicious_agents = ['sqlmap', 'nikto', 'nmap', 'masscan', 'nessus']
        for agent in suspicious_agents:
            if agent in user_agent:
                return True, f"Suspicious user agent: {agent}"
        
        return False, None
    
    @staticmethod
    def validate_request_size(request, max_size=1024*1024):  # 1MB default
        """
        Validate request size to prevent DoS attacks
        """
        content_length = request.META.get('CONTENT_LENGTH')
        if content_length:
            try:
                if int(content_length) > max_size:
                    return False, "Request too large"
            except ValueError:
                return False, "Invalid content length"
        return True, None


def security_headers_response(response):
    """
    Add security headers to response
    """
    response['X-Content-Type-Options'] = 'nosniff'
    response['X-Frame-Options'] = 'DENY'
    response['X-XSS-Protection'] = '1; mode=block'
    response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response