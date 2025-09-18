from django.test import TestCase
from offers.models import Offer

class OffersTests(TestCase):
    def setUp(self):
        Offer.objects.create(name='Solo', offer_type='solo', price_eur=50, is_active=True)
        Offer.objects.create(name='Duo', offer_type='duo', price_eur=90, is_active=True)

    def test_offers_page_lists_active_offers(self):
        resp = self.client.get('/offers/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Solo')
        self.assertContains(resp, 'Duo')

    def test_offers_api_returns_json(self):
        resp = self.client.get('/api/offers/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['content-type'].split(';')[0], 'application/json')
        data = resp.json()
        self.assertEqual(len(data), 2)
        names = {d['name'] for d in data}
        self.assertEqual(names, {'Solo','Duo'})
