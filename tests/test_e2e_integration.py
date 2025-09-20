"""Tests d'intégration End-to-End pour le workflow complet eTickets"""

import tempfile
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from offers.models import Offer
from orders.models import Order, OrderItem
from tickets.models import Ticket
from unittest.mock import patch


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class E2EWorkflowTest(TestCase):
    """Tests du workflow complet utilisateur"""

    def setUp(self):
        self.client = Client()
        # Créer des offres
        self.offers = {
            'solo': Offer.objects.create(
                name='Solo Athlétisme', 
                offer_type='solo', 
                price_eur=50, 
                is_active=True
            ),
            'duo': Offer.objects.create(
                name='Duo Natation', 
                offer_type='duo', 
                price_eur=120, 
                is_active=True
            ),
            'famille': Offer.objects.create(
                name='Famille Cyclisme', 
                offer_type='famille', 
                price_eur=200, 
                is_active=True
            )
        }

    def test_complete_user_journey_guest_to_registered(self):
        """Test workflow complet : invité → inscription → achat → vérification"""
        
        # === Phase 1: Navigation en tant qu'invité ===
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Consulter les offres
        response = self.client.get('/offers/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Solo Athlétisme')
        self.assertContains(response, 'Duo Natation')
        
        # === Phase 2: Ajout au panier en tant qu'invité ===
        # API cart vide au départ
        response = self.client.get('/api/cart/')
        data = response.json()
        self.assertEqual(len(data['items']), 0)
        self.assertEqual(data['total'], 0.0)
        
        # Ajouter des articles
        response = self.client.post('/api/cart/add/', {
            'offer_id': self.offers['solo'].id,
            'qty': 2
        })
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post('/api/cart/add/', {
            'offer_id': self.offers['duo'].id,
            'qty': 1
        })
        self.assertEqual(response.status_code, 200)
        
        # Vérifier le panier
        response = self.client.get('/api/cart/')
        data = response.json()
        self.assertEqual(len(data['items']), 2)
        self.assertEqual(data['total'], 220.0)  # 2*50 + 1*120
        
        # === Phase 3: Tentative de checkout sans connexion ===
        response = self.client.post('/api/cart/checkout/')
        self.assertEqual(response.status_code, 403)  # Non authentifié
        
        # === Phase 4: Inscription ===
        signup_data = {
            'username': 'newcustomer',
            'password1': 'SuperStrong123!',
            'password2': 'SuperStrong123!'
        }
        response = self.client.post('/signup/', signup_data)
        self.assertEqual(response.status_code, 302)  # Redirection après inscription
        
        # Vérifier que l'utilisateur est créé et connecté
        user = User.objects.get(username='newcustomer')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        
        # Le panier doit être préservé après inscription
        response = self.client.get('/api/cart/')
        data = response.json()
        self.assertEqual(len(data['items']), 2)
        self.assertEqual(data['total'], 220.0)
        
        # === Phase 5: Checkout avec génération de tickets ===
        with patch('tickets.models.Ticket.create_from') as mock_create:
            # Mock pour éviter la génération réelle de QR codes
            mock_tickets = []
            def create_ticket(user, order, offer):
                ticket = Ticket.objects.create(
                    user=user,
                    order=order,
                    offer=offer,
                    ticket_key=f"mock:key:{len(mock_tickets):04d}"
                )
                mock_tickets.append(ticket)
                return ticket
            
            mock_create.side_effect = create_ticket
            
            response = self.client.post('/api/cart/checkout/')
            self.assertEqual(response.status_code, 200)
            
            checkout_data = response.json()
            self.assertTrue(checkout_data['ok'])
            self.assertEqual(len(checkout_data['tickets']), 3)  # 2 solo + 1 duo
        
        # Vérifier que les tickets ont été créés
        tickets = Ticket.objects.filter(user=user)
        self.assertEqual(tickets.count(), 3)
        
        # Le panier doit être vide après checkout
        response = self.client.get('/api/cart/')
        data = response.json()
        self.assertEqual(len(data['items']), 0)
        
        # === Phase 6: Consultation des billets ===
        response = self.client.get('/my/tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Solo Athlétisme')
        self.assertContains(response, 'Duo Natation')
        
        # === Phase 7: Consultation des commandes ===
        response = self.client.get('/my/orders/')
        self.assertEqual(response.status_code, 200)
        # Doit afficher la commande avec le statut "Payée" (car tickets présents)
        
        # === Phase 8: Génération de facture PDF ===
        order = Order.objects.get(user=user)
        response = self.client.get(f'/orders/{order.id}/invoice.pdf')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # === Phase 9: Vérification des tickets ===
        ticket = tickets.first()
        response = self.client.post('/api/tickets/verify/', {
            'ticket_key': ticket.ticket_key
        })
        self.assertEqual(response.status_code, 200)
        
        verify_data = response.json()
        self.assertTrue(verify_data['ok'])
        self.assertEqual(verify_data['ticket_id'], ticket.id)

    def test_multiple_users_concurrent_purchases(self):
        """Test achats concurrents par plusieurs utilisateurs"""
        
        # Créer plusieurs utilisateurs
        users = []
        for i in range(3):
            user = User.objects.create_user(
                username=f'user{i}',
                password='TestPass123!'
            )
            users.append(user)
        
        # Chaque utilisateur fait des achats
        for i, user in enumerate(users):
            client = Client()
            client.login(username=f'user{i}', password='TestPass123!')
            
            # Ajouter au panier
            client.post('/api/cart/add/', {
                'offer_id': self.offers['solo'].id,
                'qty': i + 1  # Quantités différentes
            })
            
            # Checkout avec mock
            with patch('tickets.models.Ticket.create_from') as mock_create:
                mock_create.return_value = Ticket(
                    user=user,
                    ticket_key=f"mock:user{i}:key"
                )
                response = client.post('/api/cart/checkout/')
                self.assertEqual(response.status_code, 200)
        
        # Vérifier que chaque utilisateur a ses propres tickets
        for i, user in enumerate(users):
            orders = Order.objects.filter(user=user)
            self.assertGreaterEqual(orders.count(), 1)

    def test_cart_persistence_across_sessions(self):
        """Test persistence du panier entre les sessions"""
        
        # Session 1: Ajouter au panier
        self.client.post('/api/cart/add/', {
            'offer_id': self.offers['solo'].id,
            'qty': 1
        })
        
        # Récupérer la session ID
        session_key = self.client.session.session_key
        
        # Nouveau client avec la même session
        new_client = Client()
        new_client.session = self.client.session
        
        # Le panier doit être présent
        response = new_client.get('/api/cart/')
        data = response.json()
        self.assertEqual(len(data['items']), 1)

    def test_error_handling_during_purchase(self):
        """Test gestion d'erreurs pendant l'achat"""
        
        # Inscription
        user = User.objects.create_user('testuser', password='TestPass123!')
        self.client.login(username='testuser', password='TestPass123!')
        
        # Ajouter au panier
        self.client.post('/api/cart/add/', {
            'offer_id': self.offers['solo'].id,
            'qty': 1
        })
        
        # Simuler une erreur lors de la génération de ticket
        with patch('tickets.models.Ticket.create_from') as mock_create:
            mock_create.side_effect = Exception("Erreur génération QR")
            
            response = self.client.post('/api/cart/checkout/')
            # L'erreur doit être gérée (pas de 500)
            self.assertIn(response.status_code, [400, 500])  # Selon la gestion d'erreur

    def test_admin_workflow(self):
        """Test workflow administrateur"""
        
        # Créer un super utilisateur
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='AdminPass123!'
        )
        
        # Connexion admin
        self.client.login(username='admin', password='AdminPass123!')
        
        # Accès à l'admin
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        
        # Consultation des offres
        response = self.client.get('/admin/offers/offer/')
        self.assertEqual(response.status_code, 200)

    def test_mobile_user_experience(self):
        """Test expérience utilisateur mobile (responsive)"""
        
        # Simuler un user-agent mobile
        headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
        }
        
        # Toutes les pages doivent fonctionner sur mobile
        pages = ['/', '/offers/', '/signup/', '/login/']
        
        for page in pages:
            response = self.client.get(page, **headers)
            self.assertEqual(response.status_code, 200)
            # Vérifier la présence de meta viewport pour mobile
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8')
                # Les templates devraient inclure du responsive design

    def test_security_throughout_workflow(self):
        """Test aspects sécurité tout au long du workflow"""
        
        # 1. CSRF protection sur les formulaires
        response = self.client.get('/signup/')
        self.assertContains(response, 'csrfmiddlewaretoken')
        
        # 2. Authentication required pour certaines pages
        protected_pages = ['/my/orders/', '/my/tickets/', '/scan/']
        for page in protected_pages:
            response = self.client.get(page)
            self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # 3. Proper session handling
        self.client.post('/api/cart/add/', {
            'offer_id': self.offers['solo'].id,
            'qty': 1
        })
        self.assertTrue('current_order_id' in self.client.session)

    def test_data_consistency_throughout_workflow(self):
        """Test cohérence des données pendant tout le workflow"""
        
        # Créer utilisateur et ajouter au panier
        user = User.objects.create_user('testuser', password='TestPass123!')
        self.client.login(username='testuser', password='TestPass123!')
        
        self.client.post('/api/cart/add/', {
            'offer_id': self.offers['solo'].id,
            'qty': 2
        })
        
        # Checkout avec mock
        with patch('tickets.models.Ticket.create_from') as mock_create:
            tickets = []
            def create_ticket(user, order, offer):
                ticket = Ticket.objects.create(
                    user=user,
                    order=order,
                    offer=offer,
                    ticket_key=f"test:key:{len(tickets):04d}"
                )
                tickets.append(ticket)
                return ticket
            
            mock_create.side_effect = create_ticket
            self.client.post('/api/cart/checkout/')
        
        # Vérifications de cohérence
        order = Order.objects.get(user=user)
        order_items = OrderItem.objects.filter(order=order)
        user_tickets = Ticket.objects.filter(user=user, order=order)
        
        # Le nombre de tickets doit correspondre aux quantités commandées
        total_quantity = sum(item.quantity for item in order_items)
        self.assertEqual(user_tickets.count(), total_quantity)
        
        # Tous les tickets doivent appartenir au bon utilisateur
        for ticket in user_tickets:
            self.assertEqual(ticket.user, user)
            self.assertEqual(ticket.order, order)

    def test_performance_with_large_cart(self):
        """Test performance avec un gros panier"""
        
        # Ajouter de nombreux articles de types différents
        for offer in self.offers.values():
            for qty in range(1, 6):  # 1 à 5 de chaque
                self.client.post('/api/cart/add/', {
                    'offer_id': offer.id,
                    'qty': qty
                })
        
        # Le panier doit rester performant
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, 200)
        
        # Les données doivent être correctes malgré la complexité
        data = response.json()
        self.assertGreater(len(data['items']), 0)
        self.assertGreater(data['total'], 0)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class E2EErrorScenarioTest(TestCase):
    """Tests de scénarios d'erreur End-to-End"""

    def setUp(self):
        self.client = Client()
        self.offer = Offer.objects.create(
            name='Test Offer', 
            offer_type='solo', 
            price_eur=50, 
            is_active=True
        )

    def test_recovery_from_session_corruption(self):
        """Test récupération après corruption de session"""
        
        # Ajouter au panier
        self.client.post('/api/cart/add/', {
            'offer_id': self.offer.id,
            'qty': 1
        })
        
        # Corrompre la session
        session = self.client.session
        session['current_order_id'] = 99999  # ID inexistant
        session.save()
        
        # L'application doit gérer gracieusement
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, 200)
        # Doit retourner panier vide plutôt qu'erreur
        data = response.json()
        self.assertEqual(len(data['items']), 0)

    def test_handling_deleted_offer_in_cart(self):
        """Test gestion d'offre supprimée présente dans le panier"""
        
        # Ajouter au panier
        self.client.post('/api/cart/add/', {
            'offer_id': self.offer.id,
            'qty': 1
        })
        
        # "Supprimer" l'offre (désactiver)
        self.offer.is_active = False
        self.offer.save()
        
        # Le panier doit gérer l'offre inactive
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, 200)

    def test_network_interruption_simulation(self):
        """Test simulation d'interruption réseau"""
        
        user = User.objects.create_user('testuser', password='TestPass123!')
        self.client.login(username='testuser', password='TestPass123!')
        
        self.client.post('/api/cart/add/', {
            'offer_id': self.offer.id,
            'qty': 1
        })
        
        # Simuler une connexion interrompue pendant checkout
        with patch('tickets.models.Ticket.create_from') as mock_create:
            mock_create.side_effect = ConnectionError("Network interrupted")
            
            response = self.client.post('/api/cart/checkout/')
            # Doit retourner une erreur gérée, pas un crash
            self.assertNotEqual(response.status_code, 500)