import logging
import json
from datetime import datetime, timedelta
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ..decorators import admin_required
from ..utils import get_client_ip

security_logger = logging.getLogger('security')


class SecurityMonitor:
    """
    Advanced security monitoring and alerting system
    """
    
    def __init__(self):
        self.alert_thresholds = {
            'failed_logins': 10,      # per hour
            'suspicious_requests': 5,  # per hour
            'rate_limit_hits': 20,    # per hour
            'server_errors': 15,      # per hour
        }
    
    def record_security_event(self, event_type, severity, details, ip=None, user=None):
        """
        Record security event and check for alert conditions
        """
        event_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'details': details,
            'ip': ip,
            'user': user
        }
        
        # Store in cache for real-time monitoring
        cache_key = f'security_event_{datetime.now().strftime("%Y%m%d%H")}'
        events = cache.get(cache_key, [])
        events.append(event_data)
        cache.set(cache_key, events, 3600)  # 1 hour
        
        # Check for alert conditions
        self.check_alert_conditions(event_type, ip, user)
        
        # Log to file
        security_logger.error(
            f"Security Event: {event_type} - {details}",
            extra={
                'extra_ip': ip or 'Unknown',
                'extra_user': user or 'Unknown',
                'severity': severity,
                'event_type': event_type
            }
        )
    
    def check_alert_conditions(self, event_type, ip=None, user=None):
        """
        Check if alert conditions are met and send notifications
        """
        current_hour = datetime.now().strftime("%Y%m%d%H")
        cache_key = f'security_event_{current_hour}'
        events = cache.get(cache_key, [])
        
        # Count events by type in current hour
        event_counts = {}
        for event in events:
            evt_type = event['event_type']
            event_counts[evt_type] = event_counts.get(evt_type, 0) + 1
        
        # Check thresholds and send alerts
        for evt_type, threshold in self.alert_thresholds.items():
            if event_counts.get(evt_type, 0) >= threshold:
                self.send_security_alert(evt_type, event_counts[evt_type], ip, user)
    
    def send_security_alert(self, event_type, count, ip=None, user=None):
        """
        Send security alert notification
        """
        alert_key = f'alert_sent_{event_type}_{datetime.now().strftime("%Y%m%d%H")}'
        
        # Prevent duplicate alerts in same hour
        if cache.get(alert_key):
            return
        
        cache.set(alert_key, True, 3600)  # 1 hour
        
        subject = f"🚨 Security Alert: {event_type.replace('_', ' ').title()}"
        message = f"""
        Security Alert Triggered
        ========================
        
        Event Type: {event_type}
        Count: {count} in the last hour
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        IP: {ip or 'Multiple/Unknown'}
        User: {user or 'Multiple/Unknown'}
        
        Please investigate immediately.
        
        Crystals API Security System
        """
        
        # Log the alert
        security_logger.critical(
            f"SECURITY ALERT: {event_type} - Count: {count}",
            extra={
                'extra_ip': ip or 'Multiple',
                'extra_user': user or 'Multiple',
                'alert_type': event_type,
                'event_count': count
            }
        )
        
        # Send email if configured
        if hasattr(settings, 'SECURITY_ALERT_EMAIL') and settings.SECURITY_ALERT_EMAIL:
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.SECURITY_ALERT_EMAIL],
                    fail_silently=True
                )
            except Exception as e:
                security_logger.error(f"Failed to send security alert email: {str(e)}")
    
    def get_security_dashboard_data(self):
        """
        Get security dashboard data for the last 24 hours
        """
        now = datetime.now()
        dashboard_data = {
            'summary': {},
            'hourly_events': {},
            'top_ips': {},
            'recent_events': []
        }
        
        # Get events for last 24 hours
        all_events = []
        for i in range(24):
            hour = (now - timedelta(hours=i)).strftime("%Y%m%d%H")
            cache_key = f'security_event_{hour}'
            events = cache.get(cache_key, [])
            all_events.extend(events)
        
        # Calculate summary statistics
        event_types = {}
        ip_counts = {}
        hourly_counts = {}
        
        for event in all_events:
            event_type = event['event_type']
            ip = event.get('ip', 'Unknown')
            hour = event['timestamp'][:13]  # YYYY-MM-DDTHH
            
            event_types[event_type] = event_types.get(event_type, 0) + 1
            ip_counts[ip] = ip_counts.get(ip, 0) + 1
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        dashboard_data['summary'] = event_types
        dashboard_data['hourly_events'] = hourly_counts
        dashboard_data['top_ips'] = dict(sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        dashboard_data['recent_events'] = sorted(all_events, key=lambda x: x['timestamp'], reverse=True)[:50]
        
        return dashboard_data
    
    def block_ip(self, ip_address, duration_hours=24, reason="Manual block"):
        """
        Block an IP address temporarily
        """
        cache_key = f'blocked_ip_{ip_address}'
        cache.set(cache_key, {
            'blocked_at': datetime.now().isoformat(),
            'duration_hours': duration_hours,
            'reason': reason
        }, duration_hours * 3600)
        
        self.record_security_event(
            'IP_BLOCKED',
            'HIGH',
            f"IP {ip_address} blocked for {duration_hours}h: {reason}",
            ip=ip_address
        )
    
    def is_ip_blocked(self, ip_address):
        """
        Check if IP address is blocked
        """
        cache_key = f'blocked_ip_{ip_address}'
        block_info = cache.get(cache_key)
        return block_info is not None
    
    def unblock_ip(self, ip_address):
        """
        Unblock an IP address
        """
        cache_key = f'blocked_ip_{ip_address}'
        cache.delete(cache_key)
        
        self.record_security_event(
            'IP_UNBLOCKED',
            'INFO',
            f"IP {ip_address} unblocked",
            ip=ip_address
        )


# Global security monitor instance
security_monitor = SecurityMonitor()


@require_http_methods(["GET"])
@admin_required
def security_dashboard(request):
    """
    Security dashboard endpoint for admins
    """
    try:
        dashboard_data = security_monitor.get_security_dashboard_data()
        return JsonResponse({
            'status': 'success',
            'data': dashboard_data
        })
    except Exception as e:
        security_logger.error(f"Security dashboard error: {str(e)}")
        return JsonResponse({
            'error': 'Failed to load security dashboard'
        }, status=500)


@require_http_methods(["POST"])
@admin_required
def block_ip_endpoint(request):
    """
    Endpoint to manually block an IP address
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        ip_address = data.get('ip_address')
        duration_hours = data.get('duration_hours', 24)
        reason = data.get('reason', 'Manual admin block')
        
        if not ip_address:
            return JsonResponse({
                'error': 'IP address is required'
            }, status=400)
        
        security_monitor.block_ip(ip_address, duration_hours, reason)
        
        return JsonResponse({
            'status': 'success',
            'message': f'IP {ip_address} blocked for {duration_hours} hours'
        })
        
    except Exception as e:
        security_logger.error(f"Block IP error: {str(e)}")
        return JsonResponse({
            'error': 'Failed to block IP'
        }, status=500)


@require_http_methods(["POST"])
@admin_required
def unblock_ip_endpoint(request):
    """
    Endpoint to manually unblock an IP address
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        ip_address = data.get('ip_address')
        
        if not ip_address:
            return JsonResponse({
                'error': 'IP address is required'
            }, status=400)
        
        security_monitor.unblock_ip(ip_address)
        
        return JsonResponse({
            'status': 'success',
            'message': f'IP {ip_address} unblocked'
        })
        
    except Exception as e:
        security_logger.error(f"Unblock IP error: {str(e)}")
        return JsonResponse({
            'error': 'Failed to unblock IP'
        }, status=500)


@require_http_methods(["GET"])
@admin_required
def security_logs(request):
    """
    Endpoint to get recent security logs
    """
    try:
        # Get query parameters
        limit = int(request.GET.get('limit', 100))
        event_type = request.GET.get('event_type')
        
        # Get recent events from cache
        now = datetime.now()
        all_events = []
        
        for i in range(24):  # Last 24 hours
            hour = (now - timedelta(hours=i)).strftime("%Y%m%d%H")
            cache_key = f'security_event_{hour}'
            events = cache.get(cache_key, [])
            all_events.extend(events)
        
        # Filter by event type if specified
        if event_type:
            all_events = [e for e in all_events if e['event_type'] == event_type]
        
        # Sort by timestamp and limit
        all_events = sorted(all_events, key=lambda x: x['timestamp'], reverse=True)[:limit]
        
        return JsonResponse({
            'status': 'success',
            'logs': all_events,
            'total': len(all_events)
        })
        
    except Exception as e:
        security_logger.error(f"Security logs error: {str(e)}")
        return JsonResponse({
            'error': 'Failed to get security logs'
        }, status=500)