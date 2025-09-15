from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Ticket, checksum

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_ticket(request):
    key = request.data.get("ticket_key","").strip()
    if ":" not in key:
        return Response({"ok": False, "error": "format invalide"}, status=400)
    raw, chk = key.rsplit(":", 1)
    if checksum(raw) != chk:
        return Response({"ok": False, "error": "checksum invalide"}, status=400)
    try:
        t = Ticket.objects.get(ticket_key=key, user=request.user)
    except Ticket.DoesNotExist:
        return Response({"ok": False, "error": "ticket inconnu"}, status=404)
    return Response({"ok": True, "ticket_id": t.id, "offer": t.offer.name})
