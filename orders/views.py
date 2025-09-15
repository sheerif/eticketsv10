from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem
from offers.models import Offer
from .api import get_or_create_guest_user, get_or_create_order_for

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items__offer").order_by("-id")
    return render(request, "my_orders.html", {"orders": orders})

@login_required
def invoice_pdf(request, order_id: int):
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from django.http import HttpResponse
    order = get_object_or_404(Order, id=order_id, user=request.user)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, y, f"Facture #{order.id}")
    y -= 20
    p.setFont("Helvetica", 10)
    p.drawString(40, y, f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
    y -= 30
    total = 0.0
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "Articles")
    y -= 20
    p.setFont("Helvetica", 10)
    for it in order.items.select_related("offer"):
        line_total = float(it.offer.price_eur) * it.quantity
        total += line_total
        p.drawString(40, y, f"- {it.offer.name} x{it.quantity}")
        p.drawRightString(width-40, y, f"{line_total:.2f} €")
        y -= 18
        if y < 60:
            p.showPage(); y = height - 50
    y -= 10
    p.setFont("Helvetica-Bold", 12)
    p.drawRightString(width-40, y, f"Total: {total:.2f} €")
    p.showPage()
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="invoice-{order.id}.pdf"'
    return response

@csrf_exempt
def cart_add_redirect(request, offer_id: int):
    """GET fallback: /orders/cart/add/<offer_id>/?qty=1&next=/offers/

    Permet d'ajouter au panier même si les POST JS/CSRF échouent.

    """
    next_url = request.GET.get("next") or "/offers/"
    try:
        qty = int(request.GET.get("qty", "1"))
    except Exception:
        qty = 1
    user = get_or_create_guest_user(request)
    offer = get_object_or_404(Offer, id=offer_id, is_active=True)
    order = get_or_create_order_for(request, user)
    item, _ = OrderItem.objects.get_or_create(order=order, offer=offer, defaults={"quantity": 0})
    item.quantity = (item.quantity or 0) + max(qty, 1)
    item.save()
    request.session.modified = True
    return redirect(next_url)


from django.http import HttpResponseBadRequest

def _require_int(val, default=0):
    try:
        return int(val)
    except Exception:
        return default

@csrf_exempt
def cart_update_redirect(request, offer_id: int):
    """GET fallback: /orders/cart/update/<offer_id>/?qty=2&next=/offers/

    Met à jour la quantité, 0 = suppression.

    """
    next_url = request.GET.get("next") or "/offers/"
    qty = _require_int(request.GET.get("qty"), -999)
    if qty == -999:
        return HttpResponseBadRequest("qty requis")
    user = get_or_create_guest_user(request)
    offer = get_object_or_404(Offer, id=offer_id, is_active=True)
    order = get_or_create_order_for(request, user)
    from .models import OrderItem
    if qty <= 0:
        OrderItem.objects.filter(order=order, offer=offer).delete()
    else:
        item, _ = OrderItem.objects.get_or_create(order=order, offer=offer, defaults={"quantity": 0})
        item.quantity = qty
        item.save()
    request.session.modified = True
    return redirect(next_url)

@csrf_exempt
def cart_clear_redirect(request):
    """GET fallback: /orders/cart/clear/?next=/offers/  -> vide le panier
"""
    next_url = request.GET.get("next") or "/offers/"
    user = get_or_create_guest_user(request)
    order = get_or_create_order_for(request, user)
    from .models import OrderItem
    OrderItem.objects.filter(order=order).delete()
    request.session.modified = True
    return redirect(next_url)

@login_required(login_url="/login/")
def checkout_redirect(request):
    """GET /orders/checkout/ — finalise la commande (mock)
    - Si panier vide -> message + retour /offers/
    - Sinon génère les tickets et redirige vers /my/tickets/
    """
    from django.contrib import messages
    from tickets.models import Ticket
    from .api import SESSION_KEY

    order_id = request.session.get(SESSION_KEY)
    if not order_id:
        messages.warning(request, "Votre panier est vide.")
        return redirect("/offers/")
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "Commande introuvable.")
        return redirect("/offers/")

    if order.user_id != request.user.id:
        order.user = request.user
        order.save()

    if not order.items.exists():
        messages.warning(request, "Votre panier est vide.")
        return redirect("/offers/")

    # Génération des tickets (mock) — 1 ticket par quantité
    created = 0
    for it in order.items.all():
        for _ in range(it.quantity):
            Ticket.create_from(user=request.user, order=order, offer=it.offer)
            created += 1

    # Nettoie le panier
    try:
        from .api import SESSION_KEY as SK
        del request.session[SK]
        request.session.modified = True
    except Exception:
        pass

    messages.success(request, f"Paiement simulé réussi — {created} billet(s) généré(s).")
    return redirect("/my/tickets/")
