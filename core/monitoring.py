import os
import time
import json
import logging
from django.utils import timezone
from django.core.cache import cache

# Structured logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/etickets.log',
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'json' if os.getenv('DJANGO_ENV') == 'production' else 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/security.log',
            'maxBytes': 1024*1024*10,
            'backupCount': 10,
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        },
        'etickets.security': {
            'handlers': ['security'],
            'level': 'WARNING',
            'propagate': False,
        },
        'etickets.business': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

class BusinessMetrics:
    """Business metrics collector"""
    
    @staticmethod
    def track_ticket_verification(user_id, success=True, ticket_id=None):
        """Track ticket verification events"""
        logger = logging.getLogger('etickets.business')
        
        event = {
            'event': 'ticket_verification',
            'user_id': user_id,
            'success': success,
            'ticket_id': ticket_id,
            'timestamp': timezone.now().isoformat()
        }
        
        logger.info(json.dumps(event))
        
        # Update metrics cache
        today = timezone.now().date().isoformat()
        cache_key = f'metrics_verifications_{today}'
        current_count = cache.get(cache_key, 0)
        cache.set(cache_key, current_count + 1, 86400)  # 24h cache
    
    @staticmethod
    def track_purchase(user_id, order_id, total_eur, items_count):
        """Track purchase events"""
        logger = logging.getLogger('etickets.business')
        
        event = {
            'event': 'purchase_completed',
            'user_id': user_id,
            'order_id': order_id,
            'total_eur': float(total_eur),
            'items_count': items_count,
            'timestamp': timezone.now().isoformat()
        }
        
        logger.info(json.dumps(event))
        
        # Update daily revenue cache
        today = timezone.now().date().isoformat()
        revenue_key = f'metrics_revenue_{today}'
        current_revenue = cache.get(revenue_key, 0.0)
        cache.set(revenue_key, current_revenue + float(total_eur), 86400)
    
    @staticmethod
    def track_security_event(event_type, ip_address, user_id=None, details=None):
        """Track security-related events"""
        logger = logging.getLogger('etickets.security')
        
        event = {
            'event': event_type,
            'ip_address': ip_address,
            'user_id': user_id,
            'details': details,
            'timestamp': timezone.now().isoformat()
        }
        
        logger.warning(json.dumps(event))

class PerformanceMiddleware:
    """Middleware to track request performance"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # Log slow requests (> 1 second)
        if duration > 1.0:
            logger = logging.getLogger('etickets.business')
            slow_request = {
                'event': 'slow_request',
                'path': request.path,
                'method': request.method,
                'duration_seconds': round(duration, 3),
                'status_code': response.status_code,
                'user_id': request.user.id if request.user.is_authenticated else None,
                'timestamp': timezone.now().isoformat()
            }
            logger.warning(json.dumps(slow_request))
        
        # Add performance header
        response['X-Response-Time'] = f"{duration:.3f}s"
        
        return response