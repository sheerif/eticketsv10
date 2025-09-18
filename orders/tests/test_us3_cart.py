from django.test import TestCase
from offers.models import Offer

class CartApiTests(TestCase):
    def setUp(self):
        self.offer = Offer.objects.create(name="Solo", offer_type="solo", price_eur=50, is_active=True)

    def test_cart_add_and_summary(self):
        # add 2
        resp = self.client.post("/api/cart/add/", data={"offer_id": self.offer.id, "qty": 2})
        self.assertEqual(resp.status_code, 200)
        # summary
        resp = self.client.get("/api/cart/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["qty"], 2)
        self.assertAlmostEqual(data["total"], 100.0, places=2)

    def test_cart_update_and_clear(self):
        # add 1
        self.client.post("/api/cart/add/", data={"offer_id": self.offer.id, "qty": 1})
        # update to 3
        self.client.post("/api/cart/update/", data={"offer_id": self.offer.id, "qty": 3})
        resp = self.client.get("/api/cart/")
        self.assertEqual(resp.json()["items"][0]["qty"], 3)
        # clear
        self.client.post("/api/cart/clear/")
        resp = self.client.get("/api/cart/")
        self.assertEqual(resp.json()["items"], [])
