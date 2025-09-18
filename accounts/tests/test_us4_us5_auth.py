from django.test import TestCase
from django.contrib.auth.models import User

class AuthFlowTests(TestCase):
    def test_signup_then_login_logout(self):
        # signup
        resp = self.client.post("/signup/", data={
            "username": "alice",
            "password1": "StrongPassw0rd!",
            "password2": "StrongPassw0rd!",
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(User.objects.filter(username="alice").exists())

        # logout
        self.client.get("/logout/")

        # login
        resp = self.client.post("/login/", data={
            "username": "alice",
            "password": "StrongPassw0rd!"
        })
        self.assertEqual(resp.status_code, 302)  # redirect upon success
