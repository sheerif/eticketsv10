import os
import time
import hashlib
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse

def rate_limit(requests=10, window=60, per_ip=True, per_user=False):
    """
    Rate limiting decorator for API views
    
    Args:
        requests: Number of allowed requests
        window: Time window in seconds
        per_ip: Apply limit per IP address
        per_user: Apply limit per authenticated user
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Generate cache key
            key_parts = ['rate_limit', view_func.__name__]
            
            if per_ip:
                ip = get_client_ip(request)
                key_parts.append(f'ip_{ip}')
            
            if per_user and request.user.is_authenticated:
                key_parts.append(f'user_{request.user.id}')
            
            cache_key = hashlib.md5(':'.join(key_parts).encode()).hexdigest()
            
            # Check current usage
            current_requests = cache.get(cache_key, [])
            now = time.time()
            
            # Remove old requests outside window
            current_requests = [req_time for req_time in current_requests if now - req_time < window]
            
            # Check if limit exceeded
            if len(current_requests) >= requests:
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'limit': requests,
                    'window': window,
                    'retry_after': window - (now - current_requests[0])
                }, status=429)
            
            # Add current request
            current_requests.append(now)
            cache.set(cache_key, current_requests, window)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def validate_cart_data(request):
    """Enhanced validation for cart API calls"""
    data = request.data
    
    # Validate offer_id
    offer_id = data.get('offer_id')
    if not offer_id or not str(offer_id).isdigit():
        return {'error': 'Invalid offer_id'}, 400
    
    # Validate quantity
    try:
        qty = int(data.get('qty', 1))
        if qty < 0 or qty > 10:  # Max 10 tickets per offer
            return {'error': 'Invalid quantity (0-10 allowed)'}, 400
    except (ValueError, TypeError):
        return {'error': 'Invalid quantity format'}, 400
    
    return None, None

# Security headers middleware
class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # CSP for production
        if hasattr(request, 'is_secure') and request.is_secure():
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
                "img-src 'self' data:; "
                "font-src 'self' cdn.jsdelivr.net;"
            )
        
        return response