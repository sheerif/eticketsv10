from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from offers.models import Offer
from tickets.models import Ticket
import tempfile, shutil, os

@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class CartCheckoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('buyer', password='Password123!')
        self.offer = Offer.objects.create(name='Solo', offer_type='solo', price_eur=50, is_active=True)

    def test_cart_add_summary_update_clear(self):
        # add item
        r = self.client.post('/api/cart/add/', {'offer_id': self.offer.id, 'quantity': 2})
        self.assertEqual(r.status_code, 200)
        # summary
        r = self.client.get('/api/cart/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(len(data['items']), 1)
        self.assertAlmostEqual(data['total'], 100.0, places=2)
        # update
        r = self.client.post('/api/cart/update/', {'offer_id': self.offer.id, 'quantity': 1})
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/cart/')
        self.assertEqual(r.json()['total'], 50.0)
        # clear
        r = self.client.post('/api/cart/clear/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.get('/api/cart/').json()['items'], [])

    def test_checkout_creates_tickets_and_clears_cart(self):
        # login
        self.client.login(username='buyer', password='Password123!')
        # add to cart
        self.client.post('/api/cart/add/', {'offer_id': self.offer.id, 'quantity': 2})
        # checkout
        r = self.client.post('/api/cart/checkout/')
        self.assertEqual(r.status_code, 302)  # redirect to /my/tickets/
        # tickets created
        self.assertEqual(Ticket.objects.filter(user=self.user).count(), 2)
        # media file written (at least for one)
        t = Ticket.objects.filter(user=self.user).first()
        self.assertTrue(bool(t.qr_image.name))
