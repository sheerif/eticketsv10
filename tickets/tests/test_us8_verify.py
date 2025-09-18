from django.test import TestCase
from django.contrib.auth.models import User
from offers.models import Offer
from orders.models import Order
from tickets.models import Ticket, checksum

class VerifyTicketTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="eve", password="StrongPassw0rd!")
        self.offer = Offer.objects.create(name="Solo", offer_type="solo", price_eur=50, is_active=True)
        self.order = Order.objects.create(user=self.user)
        raw = "user-1:order-1"
        self.valid_key = f"{raw}:{checksum(raw)}"
        self.ticket = Ticket.objects.create(user=self.user, order=self.order, offer=self.offer, ticket_key=self.valid_key)

    def test_verify_ticket_ok(self):
        self.client.login(username="eve", password="StrongPassw0rd!")
        resp = self.client.post("/api/tickets/verify/", data={"ticket_key": self.valid_key})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("ok"))

    def test_verify_ticket_bad_checksum(self):
        self.client.login(username="eve", password="StrongPassw0rd!")
        bad_key = "user-1:order-1:deadbeef"
        resp = self.client.post("/api/tickets/verify/", data={"ticket_key": bad_key})
        self.assertEqual(resp.status_code, 400)

    def test_verify_ticket_not_found(self):
        self.client.login(username="eve", password="StrongPassw0rd!")
        # key well-formed but not existing
        raw = "unknown"
        key = f"{raw}:{checksum(raw)}"
        resp = self.client.post("/api/tickets/verify/", data={"ticket_key": key})
        self.assertEqual(resp.status_code, 404)
