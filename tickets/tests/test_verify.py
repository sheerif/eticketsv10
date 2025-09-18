from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from offers.models import Offer
from orders.models import Order, OrderItem
from tickets.models import Ticket
import tempfile

@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class VerifyTicketTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('buyer', password='Password123!')
        self.offer = Offer.objects.create(name='Solo', offer_type='solo', price_eur=50, is_active=True)
        self.order = Order.objects.create(user=self.user)
        OrderItem.objects.create(order=self.order, offer=self.offer, quantity=1)
        self.ticket = Ticket.create_from(user=self.user, order=self.order, offer=self.offer)

    def test_verify_requires_auth(self):
        r = self.client.post('/api/tickets/verify/', {'ticket_key': self.ticket.ticket_key}, content_type='application/json')
        self.assertEqual(r.status_code, 403)

    def test_verify_success_and_errors(self):
        self.client.login(username='buyer', password='Password123!')
        # OK
        r = self.client.post('/api/tickets/verify/', {'ticket_key': self.ticket.ticket_key}, content_type='application/json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json().get('ok'), True)
        # Bad format
        r = self.client.post('/api/tickets/verify/', {'ticket_key': 'INVALID'}, content_type='application/json')
        self.assertEqual(r.status_code, 400)
        # Bad checksum
        bad = self.ticket.ticket_key[:-1] + ('x' if self.ticket.ticket_key[-1]!='x' else 'y')
        r = self.client.post('/api/tickets/verify/', {'ticket_key': bad}, content_type='application/json')
        self.assertEqual(r.status_code, 400)
