from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id","user","order","offer","ticket_key")
    readonly_fields = ("ticket_key",)
