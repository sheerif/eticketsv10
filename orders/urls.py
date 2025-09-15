from django.urls import path
from .views import my_orders, invoice_pdf, cart_add_redirect, cart_update_redirect, cart_clear_redirect, checkout_redirect

urlpatterns = [
    path('orders/checkout/', checkout_redirect, name='checkout_redirect'),
    path('orders/cart/update/<int:offer_id>/', cart_update_redirect, name='cart_update_redirect'),
    path('orders/cart/clear/', cart_clear_redirect, name='cart_clear_redirect'),
    path('orders/cart/add/<int:offer_id>/', cart_add_redirect, name='cart_add_redirect'),
    path("my/orders/", my_orders, name="my_orders"),
    path("orders/<int:order_id>/invoice.pdf", invoice_pdf, name="invoice_pdf"),
]
