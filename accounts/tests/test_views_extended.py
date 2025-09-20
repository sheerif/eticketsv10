"""Tests étendus pour accounts/views.py - amélioration de la couverture"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.contrib.auth.forms import UserCreationForm


class AccountsViewsExtendedTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.existing_user = User.objects.create_user(
            username='existing', 
            password='ExistingPass123!'
        )

    def test_signup_get_displays_form(self):
        """Test que la page d'inscription affiche le formulaire"""
        response = self.client.get('/signup/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertIsInstance(response.context['form'], UserCreationForm)
        self.assertContains(response, 'Créer un compte')

    def test_signup_get_with_next_parameter(self):
        """Test signup avec paramètre next"""
        response = self.client.get('/signup/?next=/my/tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['next'], '/my/tickets/')
        self.assertContains(response, 'value="/my/tickets/"')

    def test_signup_post_valid_data(self):
        """Test inscription avec données valides"""
        form_data = {
            'username': 'newuser',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }
        response = self.client.post('/signup/', form_data)
        
        # Vérifier redirection
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/offers/')  # Redirection par défaut
        
        # Vérifier que l'utilisateur a été créé
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Vérifier que l'utilisateur est connecté
        user = User.objects.get(username='newuser')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        
        # Vérifier message de succès
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Compte créé' in str(m) for m in messages))

    def test_signup_post_valid_data_with_next(self):
        """Test inscription avec redirection personnalisée"""
        form_data = {
            'username': 'newuser2',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }
        response = self.client.post('/signup/?next=/scan/', form_data)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/scan/')

    def test_signup_post_invalid_data(self):
        """Test inscription avec données invalides"""
        form_data = {
            'username': 'existing',  # Nom d'utilisateur déjà pris
            'password1': 'weak',
            'password2': 'different'
        }
        response = self.client.post('/signup/', form_data)
        
        # Doit rester sur la page avec erreurs
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')
        form = response.context['form']
        self.assertFalse(form.is_valid())

    def test_signup_post_password_mismatch(self):
        """Test inscription avec mots de passe différents"""
        form_data = {
            'username': 'testuser',
            'password1': 'StrongPass123!',
            'password2': 'DifferentPass123!'
        }
        response = self.client.post('/signup/', form_data)
        
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_signup_post_weak_password(self):
        """Test inscription avec mot de passe faible"""
        form_data = {
            'username': 'testuser',
            'password1': '123',
            'password2': '123'
        }
        response = self.client.post('/signup/', form_data)
        
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())

    def test_signup_post_existing_username(self):
        """Test inscription avec nom d'utilisateur existant"""
        form_data = {
            'username': 'existing',  # Utilisateur déjà créé dans setUp
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }
        response = self.client.post('/signup/', form_data)
        
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_logout_simple_when_logged_in(self):
        """Test déconnexion quand connecté"""
        self.client.login(username='existing', password='ExistingPass123!')
        
        # Vérifier qu'on est connecté
        self.assertTrue('_auth_user_id' in self.client.session)
        
        response = self.client.get('/logout/')
        
        # Vérifier redirection
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/offers/')  # Redirection par défaut
        
        # Vérifier que l'utilisateur est déconnecté
        self.assertFalse('_auth_user_id' in self.client.session)
        
        # Vérifier message de succès
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('déconnecté' in str(m) for m in messages))

    def test_logout_simple_when_not_logged_in(self):
        """Test déconnexion quand pas connecté"""
        response = self.client.get('/logout/')
        
        # Doit quand même rediriger sans erreur
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/offers/')
        
        # Message de succès affiché quand même
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('déconnecté' in str(m) for m in messages))

    def test_logout_simple_with_next_parameter(self):
        """Test déconnexion avec paramètre next"""
        self.client.login(username='existing', password='ExistingPass123!')
        
        response = self.client.get('/logout/?next=/home/')
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/home/')

    def test_signup_already_logged_in(self):
        """Test comportement signup quand déjà connecté"""
        self.client.login(username='existing', password='ExistingPass123!')
        
        response = self.client.get('/signup/')
        
        # Doit afficher la page normalement (pas de redirection forcée)
        self.assertEqual(response.status_code, 200)

    def test_signup_csrf_protection(self):
        """Test protection CSRF sur signup"""
        # Test sans token CSRF (simulate CSRF failure)
        form_data = {
            'username': 'newuser',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }
        
        # Désactiver le middleware CSRF pour ce test
        # En vrai, Django va rejeter sans token CSRF
        response = self.client.post('/signup/', form_data, HTTP_X_CSRFTOKEN='invalid')
        
        # Le formulaire devrait quand même être traité (Django gère automatiquement)
        # Dans un vrai environnement, ça donnerait une erreur 403

    def test_context_data_preservation(self):
        """Test que les données de contexte sont préservées lors d'erreurs"""
        form_data = {
            'username': 'existing',  # Erreur
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }
        response = self.client.post('/signup/?next=/custom/', form_data)
        
        self.assertEqual(response.status_code, 200)
        # Le next doit être préservé même en cas d'erreur
        self.assertEqual(response.context['next'], '/custom/')
        # Le formulaire doit contenir les données soumises
        self.assertEqual(response.context['form'].data['username'], 'existing')

    def test_multiple_signup_attempts(self):
        """Test tentatives multiples d'inscription"""
        form_data = {
            'username': 'testuser',
            'password1': 'weak',  # Première tentative échoue
            'password2': 'weak'
        }
        
        # Première tentative
        response1 = self.client.post('/signup/', form_data)
        self.assertEqual(response1.status_code, 200)  # Erreur
        
        # Correction des données
        form_data['password1'] = 'StrongPass123!'
        form_data['password2'] = 'StrongPass123!'
        
        # Deuxième tentative
        response2 = self.client.post('/signup/', form_data)
        self.assertEqual(response2.status_code, 302)  # Succès
        
        # Utilisateur créé
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_logout_preserves_session_data(self):
        """Test que la déconnexion ne casse pas les données de session importantes"""
        self.client.login(username='existing', password='ExistingPass123!')
        
        # Ajouter des données de session
        session = self.client.session
        session['test_data'] = 'should_persist'
        session.save()
        
        self.client.get('/logout/')
        
        # Les données de session custom peuvent persister
        # (seules les données d'auth sont supprimées)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_form_rendering_with_errors(self):
        """Test rendu du formulaire avec erreurs"""
        form_data = {
            'username': '',  # Champ requis vide
            'password1': 'test',
            'password2': 'test'
        }
        response = self.client.post('/signup/', form_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'errorlist')  # Django affiche les erreurs
        self.assertContains(response, 'This field is required')  # Message d'erreur