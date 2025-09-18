from django.test import TestCase
from django.urls import reverse
from offers.models import Offer

class OffersPageTest(TestCase):
    def setUp(self):
        Offer.objects.create(name="Solo", offer_type="solo", price_eur=50, is_active=True)
        Offer.objects.create(name="Duo", offer_type="duo", price_eur=90, is_active=True)

    def test_offers_page_status_and_context(self):
        resp = self.client.get("/offers/")  # reverse('offers_page') si nommé
        self.assertEqual(resp.status_code, 200)
        self.assertIn("offers", resp.context)
        self.assertEqual(resp.context["offers"].count(), 2)
