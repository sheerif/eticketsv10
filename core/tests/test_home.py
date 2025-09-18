from django.test import TestCase
from django.urls import reverse

class HomePageTest(TestCase):
    def test_home_status_and_csrf_cookie(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        # ensure_csrf_cookie decorateur -> cookie devrait exister
        self.assertIn('csrftoken', resp.cookies)
