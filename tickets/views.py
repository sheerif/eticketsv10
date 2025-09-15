from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Ticket

def scan_page(request):
    return render(request, "scan.html")

@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(user=request.user).select_related("offer","order").order_by("-id")
    return render(request, "my_tickets.html", {"tickets": tickets})
