from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.core.cache import cache
from .models import Ticket, checksum

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_ticket(request):
    key = request.data.get("ticket_key","").strip()
    
    # Enhanced validation
    if not key:
        return Response({"ok": False, "error": "Clé de ticket requise"}, status=400)
    
    if len(key) > 200:  # Prevent DoS with huge keys
        return Response({"ok": False, "error": "Clé trop longue"}, status=400)
        
    if ":" not in key:
        return Response({"ok": False, "error": "Format invalide"}, status=400)
    
    raw, chk = key.rsplit(":", 1)
    
    # Check cache first to avoid database hit
    cache_key = f"ticket_verify_{key[:20]}"  # Use first 20 chars as cache key
    cached_result = cache.get(cache_key)
    if cached_result:
        return Response(cached_result)
    
    # Verify checksum
    if checksum(raw) != chk:
        error_result = {"ok": False, "error": "Checksum invalide"}
        cache.set(cache_key, error_result, 60)  # Cache failed attempts for 1 minute
        return Response(error_result, status=400)
    
    try:
        # Optimized query with select_related
        ticket = Ticket.objects.select_related('offer', 'user', 'order').get(
            ticket_key=key, 
            user=request.user
        )
        
        # Update verification timestamp
        ticket.verified_at = timezone.now()
        ticket.save(update_fields=['verified_at'])
        
        success_result = {
            "ok": True, 
            "ticket_id": ticket.id, 
            "offer": ticket.offer.name,
            "verified_at": ticket.verified_at.isoformat()
        }
        
        # Cache successful verification for 5 minutes
        cache.set(cache_key, success_result, 300)
        return Response(success_result)
        
    except Ticket.DoesNotExist:
        error_result = {"ok": False, "error": "Ticket inconnu ou non autorisé"}
        cache.set(cache_key, error_result, 60)
        return Response(error_result, status=404)
