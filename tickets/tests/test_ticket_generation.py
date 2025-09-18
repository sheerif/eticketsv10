from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from offers.models import Offer
from orders.models import Order
from tickets.models import Ticket
import tempfile

@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TicketGenerationTests(TestCase):
    def test_ticket_key_and_qr_saved(self):
        user = User.objects.create_user('u', password='Password123!')
        offer = Offer.objects.create(name='Solo', offer_type='solo', price_eur=50, is_active=True)
        order = Order.objects.create(user=user)
        t = Ticket.create_from(user=user, order=order, offer=offer)
        self.assertIn(':', t.ticket_key)  # contient checksum séparé
        self.assertTrue(t.qr_image.name)
