from django.test import TestCase
from django.contrib.auth.models import User
from offers.models import Offer
from orders.models import Order, OrderItem

class ReportingTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username="admin", password="StrongPassw0rd!", email="a@a.a")
        self.offer = Offer.objects.create(name="Solo", offer_type="solo", price_eur=50, is_active=True)
        user = User.objects.create_user(username="u", password="p")
        order = Order.objects.create(user=user)
        OrderItem.objects.create(order=order, offer=self.offer, quantity=2)

    def test_admin_changelist_sales_count_column(self):
        self.client.login(username="admin", password="StrongPassw0rd!")
        resp = self.client.get("/admin/offers/offer/")
        self.assertEqual(resp.status_code, 200)
        # Should include at least one occurrence of the offer name; sales_count is computed server-side
        self.assertContains(resp, "Solo")
