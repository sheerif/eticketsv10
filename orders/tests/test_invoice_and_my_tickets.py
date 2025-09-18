from django.test import TestCase
from django.contrib.auth.models import User
from offers.models import Offer
from orders.models import Order, OrderItem

class InvoiceAndMyTicketsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="john", password="StrongPassw0rd!")
        self.offer = Offer.objects.create(name="Solo", offer_type="solo", price_eur=50, is_active=True)

    def test_invoice_pdf(self):
        order = Order.objects.create(user=self.user)
        OrderItem.objects.create(order=order, offer=self.offer, quantity=1)
        self.client.login(username="john", password="StrongPassw0rd!")
        resp = self.client.get(f"/orders/{order.id}/invoice.pdf")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("application/pdf", resp["Content-Type"])

    def test_my_tickets_requires_login(self):
        resp = self.client.get("/my/tickets/")
        self.assertEqual(resp.status_code, 302)  # redirect to login
