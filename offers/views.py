from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Offer

@ensure_csrf_cookie
def offers_page(request):
    offers = Offer.objects.filter(is_active=True).order_by("price_eur")
    return render(request, "offers.html", {"offers": offers})
