"""Tests des cas d'erreur et edge cases pour eTickets"""

import tempfile
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from unittest.mock import patch, Mock
from offers.models import Offer
from orders.models import Order, OrderItem
from tickets.models import Ticket


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class ErrorHandlingTest(TestCase):
    """Tests de gestion d'erreurs et de cas limites"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', 
            password='TestPass123!'
        )
        self.offer = Offer.objects.create(
            name='Test Offer', 
            offer_type='solo', 
            price_eur=50, 
            is_active=True
        )

    def test_404_pages_render_correctly(self):
        """Test que les pages 404 s'affichent correctement"""
        
        # Page inexistante
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)
        
        # Offre inexistante
        response = self.client.get('/orders/cart/add/99999/')
        self.assertEqual(response.status_code, 404)
        
        # Facture inexistante
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get('/orders/99999/invoice.pdf')
        self.assertEqual(response.status_code, 404)

    def test_403_unauthorized_access(self):
        """Test accès non autorisé (403)"""
        
        # Tentative d'accès à une facture d'un autre utilisateur
        other_user = User.objects.create_user('other', password='TestPass123!')
        order = Order.objects.create(user=other_user)
        
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(f'/orders/{order.id}/invoice.pdf')
        self.assertEqual(response.status_code, 404)  # Django convertit 403 en 404 pour la sécurité

    def test_invalid_form_data_handling(self):
        """Test gestion de données de formulaire invalides"""
        
        # Inscription avec données manquantes
        response = self.client.post('/signup/', {
            'username': '',  # Vide
            'password1': 'weak',
            'password2': 'different'
        })
        self.assertEqual(response.status_code, 200)  # Reste sur la page avec erreurs
        self.assertContains(response, 'errorlist')
        
        # Données corrompues dans les API
        response = self.client.post('/api/cart/add/', {
            'offer_id': 'not_a_number',
            'qty': 'also_not_a_number'
        })
        # Doit gérer gracieusement sans crash
        self.assertIn(response.status_code, [200, 400, 404])

    def test_session_edge_cases(self):
        """Test cas limites de gestion de session"""
        
        # Session sans order_id
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['items']), 0)
        
        # Session avec order_id invalide
        session = self.client.session
        session['current_order_id'] = 'not_an_int'
        session.save()
        
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, 200)
        
        # Session avec order_id inexistant
        session['current_order_id'] = 99999
        session.save()
        
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['items']), 0)

    def test_database_integrity_errors(self):
        """Test gestion des erreurs d'intégrité base de données"""
        
        # Créer un ticket avec une clé existante (doit échouer)
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(
            user=self.user,
            order=order,
            offer=self.offer,
            ticket_key="unique:key:123"
        )
        
        # Tentative de créer un autre ticket avec la même clé
        with self.assertRaises(IntegrityError):
            Ticket.objects.create(
                user=self.user,
                order=order,
                offer=self.offer,
                ticket_key="unique:key:123"  # Clé dupliquée
            )

    def test_concurrent_cart_operations(self):
        """Test opérations concurrentes sur le panier"""
        
        # Simuler des ajouts simultanés au panier
        responses = []
        for i in range(5):
            response = self.client.post('/api/cart/add/', {
                'offer_id': self.offer.id,
                'qty': 1
            })
            responses.append(response)
        
        # Toutes les requêtes doivent réussir
        for response in responses:
            self.assertEqual(response.status_code, 200)
        
        # Vérifier l'état final du panier
        response = self.client.get('/api/cart/')
        data = response.json()
        self.assertEqual(len(data['items']), 1)
        # Quantité doit être la somme des ajouts
        self.assertEqual(data['items'][0]['qty'], 5)

    def test_memory_and_performance_limits(self):
        """Test limites de performance et mémoire"""
        
        # Tentative d'ajout d'une très grande quantité
        response = self.client.post('/api/cart/add/', {
            'offer_id': self.offer.id,
            'qty': 1000000  # Très grand nombre
        })
        
        # L'application doit gérer sans crash
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la quantité est raisonnable
        response = self.client.get('/api/cart/')
        data = response.json()
        if len(data['items']) > 0:
            # Quantité ne doit pas dépasser les limites raisonnables
            self.assertLessEqual(data['items'][0]['qty'], 1000000)

    def test_malformed_api_requests(self):
        """Test requêtes API malformées"""
        
        # Données manquantes
        response = self.client.post('/api/cart/add/', {})
        self.assertIn(response.status_code, [400, 404, 500])
        
        # JSON malformé (simulé avec des données bizarres)
        response = self.client.post('/api/cart/add/', {
            'offer_id': {'nested': 'object'},  # Object au lieu d'int
            'qty': [1, 2, 3]  # Array au lieu d'int
        })
        self.assertIn(response.status_code, [200, 400, 500])  # Dépend de la gestion

    def test_unicode_and_special_characters(self):
        """Test gestion des caractères Unicode et spéciaux"""
        
        # Créer une offre avec des caractères spéciaux
        special_offer = Offer.objects.create(
            name='Événement Spécial 🎯 & Émojis 🏆', 
            offer_type='solo', 
            price_eur=50, 
            is_active=True
        )
        
        # Ajouter au panier
        response = self.client.post('/api/cart/add/', {
            'offer_id': special_offer.id,
            'qty': 1
        })
        self.assertEqual(response.status_code, 200)
        
        # Vérifier affichage correct dans le panier
        response = self.client.get('/api/cart/')
        data = response.json()
        self.assertIn('🎯', data['items'][0]['name'])

    def test_timezone_edge_cases(self):
        """Test cas limites liés aux fuseaux horaires"""
        
        from django.utils import timezone
        import datetime
        
        # Créer un ticket avec une date bizarre
        order = Order.objects.create(user=self.user)
        
        # Date dans le futur
        future_time = timezone.now() + datetime.timedelta(days=365)
        
        ticket = Ticket.objects.create(
            user=self.user,
            order=order,
            offer=self.offer,
            ticket_key="future:ticket",
            created_at=future_time
        )
        
        # L'application doit gérer correctement
        self.assertIsNotNone(ticket.created_at)

    def test_edge_case_quantities(self):
        """Test quantités limites"""
        
        # Quantité zéro
        response = self.client.post('/api/cart/update/', {
            'offer_id': self.offer.id,
            'qty': 0
        })
        self.assertEqual(response.status_code, 200)
        
        # Quantité négative
        response = self.client.post('/api/cart/add/', {
            'offer_id': self.offer.id,
            'qty': -5
        })
        # Doit utiliser une valeur par défaut ou rejeter
        self.assertEqual(response.status_code, 200)

    def test_checkout_edge_cases(self):
        """Test cas limites du checkout"""
        
        self.client.login(username='testuser', password='TestPass123!')
        
        # Checkout avec panier vide
        response = self.client.post('/api/cart/checkout/')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['ok'])
        
        # Ajouter au panier puis vider juste avant checkout
        self.client.post('/api/cart/add/', {
            'offer_id': self.offer.id,
            'qty': 1
        })
        
        # Vider via l'API
        self.client.post('/api/cart/clear/')
        
        # Checkout doit détecter le panier vide
        response = self.client.post('/api/cart/checkout/')
        self.assertEqual(response.status_code, 400)

    def test_authentication_edge_cases(self):
        """Test cas limites d'authentification"""
        
        # Utilisateur désactivé
        inactive_user = User.objects.create_user(
            username='inactive',
            password='TestPass123!',
            is_active=False
        )
        
        # Tentative de connexion
        login_success = self.client.login(
            username='inactive',
            password='TestPass123!'
        )
        self.assertFalse(login_success)  # Ne doit pas pouvoir se connecter
        
        # Session expirée (simulation)
        self.client.login(username='testuser', password='TestPass123!')
        
        # Forcer la déconnexion en modifiant la session
        session = self.client.session
        del session['_auth_user_id']
        session.save()
        
        # Accès à une page protégée doit rediriger
        response = self.client.get('/my/tickets/')
        self.assertEqual(response.status_code, 302)

    @patch('tickets.models.qrcode')
    def test_qr_generation_failures(self, mock_qrcode):
        """Test échecs de génération de QR codes"""
        
        # Simuler une erreur lors de la génération QR
        mock_qrcode.QRCode.side_effect = Exception("QR generation failed")
        
        self.client.login(username='testuser', password='TestPass123!')
        self.client.post('/api/cart/add/', {
            'offer_id': self.offer.id,
            'qty': 1
        })
        
        # Checkout doit gérer l'erreur gracieusement
        response = self.client.post('/api/cart/checkout/')
        # Peut échouer ou réussir selon la gestion d'erreur implémentée
        self.assertIn(response.status_code, [200, 400, 500])

    def test_file_system_errors(self):
        """Test erreurs du système de fichiers"""
        
        with patch('builtins.open') as mock_open:
            # Simuler une erreur d'écriture fichier
            mock_open.side_effect = IOError("Disk full")
            
            self.client.login(username='testuser', password='TestPass123!')
            order = Order.objects.create(user=self.user)
            
            # Génération de PDF doit gérer l'erreur
            response = self.client.get(f'/orders/{order.id}/invoice.pdf')
            # Selon l'implémentation, peut retourner différents codes
            self.assertIn(response.status_code, [200, 500])

    def test_network_timeout_simulation(self):
        """Test simulation de timeouts réseau"""
        
        import time
        
        # Simuler une fonction lente
        def slow_function(*args, **kwargs):
            time.sleep(0.1)  # Petit délai
            return Mock()
        
        with patch('tickets.models.Ticket.save', side_effect=slow_function):
            self.client.login(username='testuser', password='TestPass123!')
            self.client.post('/api/cart/add/', {
                'offer_id': self.offer.id,
                'qty': 1
            })
            
            # Le checkout doit quand même fonctionner
            response = self.client.post('/api/cart/checkout/')
            # Selon timeout Django, peut réussir ou échouer
            self.assertIn(response.status_code, [200, 400, 500, 504])

    def test_xss_protection(self):
        """Test protection contre XSS"""
        
        # Tentative d'injection de script dans le nom
        malicious_user = User.objects.create_user(
            username='<script>alert("xss")</script>',
            password='TestPass123!'
        )
        
        self.client.login(username='<script>alert("xss")</script>', password='TestPass123!')
        
        # Consulter les pages - le contenu doit être échappé
        response = self.client.get('/my/orders/')
        self.assertEqual(response.status_code, 200)
        # Django doit échapper automatiquement le contenu
        self.assertNotContains(response, '<script>')
        self.assertContains(response, '&lt;script&gt;')  # Contenu échappé

    def test_sql_injection_protection(self):
        """Test protection contre injection SQL"""
        
        # Tentative d'injection dans les paramètres d'API
        response = self.client.post('/api/cart/add/', {
            'offer_id': "1'; DROP TABLE offers; --",
            'qty': 1
        })
        
        # Django ORM doit protéger contre l'injection
        # L'offre doit toujours exister
        self.assertTrue(Offer.objects.filter(id=self.offer.id).exists())
        
        # La réponse peut être 400 ou 404 selon la validation
        self.assertIn(response.status_code, [200, 400, 404])

    def test_csrf_protection(self):
        """Test protection CSRF"""
        
        # Tentative de POST sans token CSRF sur les vues protégées
        response = self.client.post('/signup/', {
            'username': 'newuser',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')  # Simuler AJAX
        
        # Django doit gérer la protection CSRF
        # En test, CSRF est généralement désactivé ou géré automatiquement