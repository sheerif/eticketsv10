from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ("id","user","created_at","purchase_key","total_display")
    def total_display(self, obj):
        return f"{obj.total_eur():.2f} €"
