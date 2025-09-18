from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class AuthFlowTests(TestCase):
    def test_signup_password_policy(self):
        # mot de passe trop court -> invalide
        short = {'username':'u1','password1':'short','password2':'short'}
        resp = self.client.post('/signup/', short)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Ce mot de passe est trop court', status_code=200)
        # mot de passe valide
        good = {'username':'userlong','password1':'LongPassword123!', 'password2':'LongPassword123!'}
        resp = self.client.post('/signup/?next=/offers/', good, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(User.objects.filter(username='userlong').exists())
        # connecté et redirigé
        self.assertContains(resp, 'Offres')

    def test_login_logout(self):
        User.objects.create_user('john', password='Password123!')
        # Login
        resp = self.client.post('/login/?next=/offers/', {'username':'john','password':'Password123!'}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Offres')
        # Logout
        resp = self.client.get('/logout/?next=/offers/', follow=True)
        self.assertEqual(resp.status_code, 200)
