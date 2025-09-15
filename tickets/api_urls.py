from django.urls import path
from .api import verify_ticket

urlpatterns = [
    path("tickets/verify/", verify_ticket, name="verify_ticket"),
]
