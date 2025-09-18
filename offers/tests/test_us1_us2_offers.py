from django.test import TestCase
from django.urls import reverse
from offers.models import Offer

class OffersPageTests(TestCase):
    def setUp(self):
        Offer.objects.create(name="Solo", offer_type="solo", price_eur=50, is_active=True)
        Offer.objects.create(name="Duo", offer_type="duo", price_eur=90, is_active=True)

    def test_offers_page_200_and_lists_active_offers(self):
        resp = self.client.get("/offers/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("offers", resp.context)
        names = [o.name for o in resp.context["offers"]]
        self.assertEqual(names, ["Solo", "Duo"])
