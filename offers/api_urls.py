from django.urls import path
from .api import offers_list
from orders.api import cart_add, checkout, cart_summary, cart_update, cart_clear
urlpatterns = [
    path("offers/", offers_list, name="offers_list"),
    path("cart/", cart_summary, name="cart_summary"),
    path("cart/add/", cart_add, name="cart_add"),
    path("cart/update/", cart_update, name="cart_update"),
    path("cart/clear/", cart_clear, name="cart_clear"),
    path("cart/checkout/", checkout, name="checkout"),
]
