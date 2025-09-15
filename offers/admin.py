from django.contrib import admin
from .models import Offer
from orders.models import OrderItem
from django.db.models import Count

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("name","offer_type","price_eur","is_active","sales_count")
    list_filter = ("offer_type","is_active")
    search_fields = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_sales=Count("orderitem"))

    def sales_count(self, obj):
        return getattr(obj, "_sales", 0)
    sales_count.short_description = "Ventes"
