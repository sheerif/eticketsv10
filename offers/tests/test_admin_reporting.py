from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from offers.models import Offer
from orders.models import Order, OrderItem

class AdminReportingTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin','a@a.com','Password123!')
        self.client.login(username='admin', password='Password123!')
        self.offer = Offer.objects.create(name='Solo', offer_type='solo', price_eur=50, is_active=True)
        # make some sales
        user = User.objects.create_user('u1', password='Password123!')
        order = Order.objects.create(user=user)
        OrderItem.objects.create(order=order, offer=self.offer, quantity=1)

    def test_offer_admin_list_shows_sales_count(self):
        resp = self.client.get('/admin/offers/offer/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Ventes')
