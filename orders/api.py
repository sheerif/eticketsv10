from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from offers.models import Offer
from .models import Order, OrderItem
from tickets.models import Ticket

SESSION_KEY = "current_order_id"
GUEST_KEY = "guest_user_id"

def get_or_create_guest_user(request):
    if request.user.is_authenticated:
        return request.user
    uid = request.session.get(GUEST_KEY)
    if uid:
        try:
            return User.objects.get(id=uid)
        except User.DoesNotExist:
            pass
    username = f"guest-{get_random_string(16)}"
    user = User.objects.create_user(username=username)
    user.set_unusable_password()
    user.save()
    request.session[GUEST_KEY] = user.id
    request.session.modified = True
    return user

def get_or_create_order_for(request, user):
    order_id = request.session.get(SESSION_KEY)
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            if order.user_id != user.id:
                order.user = user   # adopt guest order to authed user
                order.save()
            return order
        except Order.DoesNotExist:
            pass
    order = Order.objects.create(user=user)
    request.session[SESSION_KEY] = order.id
    request.session.modified = True
    return order

@api_view(["GET"])
@permission_classes([AllowAny])
def cart_summary(request):
    user = get_or_create_guest_user(request)
    order_id = request.session.get(SESSION_KEY)
    if not order_id:
        return Response({"items": [], "total": 0.0})
    try:
        # Optimized: use select_related to avoid N+1 queries
        order = Order.objects.select_related('user').get(id=order_id)
    except Order.DoesNotExist:
        return Response({"items": [], "total": 0.0})
    
    # Optimized: prefetch related offer data in one query
    items = [{
        "offer_id": it.offer_id,
        "name": it.offer.name,
        "price": float(it.offer.price_eur) if it.offer.price_eur is not None else 0.0,
        "qty": it.quantity if it.quantity is not None else 0,
        "line_total": float(it.offer.price_eur * it.quantity) if (it.offer.price_eur is not None and it.quantity is not None) else 0.0,
    } for it in order.items.select_related("offer")]
    
    total = sum(i["line_total"] for i in items)
    return Response({"items": items, "total": total})

@api_view(["POST"])
@permission_classes([AllowAny])
def cart_add(request):
    user = get_or_create_guest_user(request)
    offer_id = request.data.get("offer_id")
    try:
        qty = int(request.data.get("qty", 1))
    except Exception:
        qty = 1
    offer = get_object_or_404(Offer, id=offer_id, is_active=True)

    order = get_or_create_order_for(request, user)
    item, created = OrderItem.objects.get_or_create(order=order, offer=offer, defaults={"quantity": 0})
    item.quantity = (item.quantity or 0) + max(qty, 1)
    item.save()
    request.session.modified = True
    return Response({"ok": True, "order_id": order.id})

@api_view(["POST"])
@permission_classes([AllowAny])
def cart_update(request):
    user = get_or_create_guest_user(request)
    offer_id = request.data.get("offer_id")
    try:
        qty = int(request.data.get("qty", 0))
    except Exception:
        qty = 0
    order_id = request.session.get(SESSION_KEY)
    if not order_id:
        return Response({"ok": True})
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"ok": True})
    try:
        item = OrderItem.objects.get(order=order, offer_id=offer_id)
    except OrderItem.DoesNotExist:
        return Response({"ok": True})
    if qty <= 0:
        item.delete()
    else:
        item.quantity = qty
        item.save()
    request.session.modified = True
    return Response({"ok": True})

@api_view(["POST"])
@permission_classes([AllowAny])
def cart_clear(request):
    try:
        del request.session[SESSION_KEY]
        request.session.modified = True
    except KeyError:
        pass
    return Response({"ok": True})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def checkout(request):
    user = request.user
    order_id = request.session.get(SESSION_KEY)
    if not order_id:
        return Response({"ok": False, "error": "Panier vide"}, status=400)
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"ok": False, "error": "Commande introuvable"}, status=400)

    if order.user_id != user.id:
        order.user = user
        order.save()

    if not order.items.exists():
        return Response({"ok": False, "error": "Aucun article"}, status=400)

    created = []
    for it in order.items.all():
        for _ in range(it.quantity):
            t = Ticket.create_from(user=user, order=order, offer=it.offer)
            created.append(t.id)

    try:
        del request.session[SESSION_KEY]
        request.session.modified = True
    except KeyError:
        pass

    return Response({"ok": True, "order_id": order.id, "tickets": created})
