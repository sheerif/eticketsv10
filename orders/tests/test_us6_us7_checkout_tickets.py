from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch
from offers.models import Offer
from orders.models import Order, OrderItem
from orders.api import SESSION_KEY
from tickets.models import Ticket

class CheckoutTicketTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bob", password="StrongPassw0rd!")
        self.offer = Offer.objects.create(name="Solo", offer_type="solo", price_eur=50, is_active=True)

    def test_checkout_requires_auth_and_nonempty_cart(self):
        # empty cart
        resp = self.client.post("/api/cart/checkout/")
        self.assertEqual(resp.status_code, 403)  # permission IsAuthenticated

        # login
        self.client.login(username="bob", password="StrongPassw0rd!")

        # still empty cart -> 400
        resp = self.client.post("/api/cart/checkout/")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json().get("ok"), False)

    def test_checkout_creates_tickets_with_patch(self):
        # login and prepare an order in session
        self.client.login(username="bob", password="StrongPassw0rd!")
        # use the API to add items (ensures session values are set)
        self.client.post("/api/cart/add/", data={"offer_id": self.offer.id, "qty": 2})

        # Patch Ticket.create_from to avoid QR side effects and missing fields
        def fake_create_from(user, order, offer):
            # Create minimal Ticket bypassing QR
            t = Ticket.objects.create(user=user, order=order, offer=offer, ticket_key="dummy:abcd1234")
            return t

        with patch("orders.api.Ticket.create_from", side_effect=fake_create_from):
            resp = self.client.post("/api/cart/checkout/")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertTrue(data.get("ok"))
            self.assertEqual(len(data.get("tickets", [])), 2)
