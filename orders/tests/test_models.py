from django.test import TestCase
from django.contrib.auth.models import User
from offers.models import Offer
from orders.models import Order, OrderItem

class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u', password='p4ssword!')
        self.offer = Offer.objects.create(name='Solo', offer_type='solo', price_eur=50)

    def test_order_total(self):
        order = Order.objects.create(user=self.user)
        OrderItem.objects.create(order=order, offer=self.offer, quantity=2)
        self.assertEqual(order.total_eur(), 100.0)
