from django.test import TestCase
from offers.models import Offer

class OfferModelTest(TestCase):
    def test_str(self):
        o = Offer.objects.create(name="Solo", offer_type="solo", price_eur=50)
        self.assertIn("Solo", str(o))
        self.assertIn("solo", str(o))
