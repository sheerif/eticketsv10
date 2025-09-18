from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from offers.models import Offer

class AdminOfferTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username="admin", password="StrongPassw0rd!", email="a@a.a")

    def test_admin_offer_changelist(self):
        self.client.login(username="admin", password="StrongPassw0rd!")
        resp = self.client.get("/admin/offers/offer/")
        self.assertEqual(resp.status_code, 200)

    def test_admin_offer_add(self):
        self.client.login(username="admin", password="StrongPassw0rd!")
        resp = self.client.post("/admin/offers/offer/add/", data={
            "name": "Familiale",
            "offer_type": "familiale",
            "price_eur": "150.00",
            "is_active": "on",
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Offer.objects.filter(name="Familiale").exists())
