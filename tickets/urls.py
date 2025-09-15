from django.urls import path
from .views import scan_page, my_tickets

urlpatterns = [
    path("scan/", scan_page, name="scan_page"),
    path("my/tickets/", my_tickets, name="my_tickets"),
]
