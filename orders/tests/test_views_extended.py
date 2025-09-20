"""Tests étendus pour orders/views.py - amélioration de la couverture"""

import tempfile
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
from offers.models import Offer
from orders.models import Order, OrderItem
from tickets.models import Ticket


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class OrdersViewsExtendedTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', 
            password='TestPass123!',
            email='test@example.com'
        )
        self.offer1 = Offer.objects.create(
            name='Solo Athlétisme', 
            offer_type='solo', 
            price_eur=50, 
            is_active=True
        )
        self.offer2 = Offer.objects.create(
            name='Duo Natation', 
            offer_type='duo', 
            price_eur=120, 
            is_active=True
        )
        # Créer une commande avec articles
        self.order = Order.objects.create(user=self.user)
        OrderItem.objects.create(order=self.order, offer=self.offer1, quantity=2)
        OrderItem.objects.create(order=self.order, offer=self.offer2, quantity=1)

    def test_my_orders_requires_login(self):
        """Test que my_orders nécessite une authentification"""
        response = self.client.get('/my/orders/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_my_orders_displays_user_orders(self):
        """Test l'affichage des commandes utilisateur"""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get('/my/orders/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Solo Athlétisme')
        self.assertContains(response, 'Duo Natation')
        self.assertContains(response, self.order.created_at.strftime('%d/%m/%Y'))
    
    def test_my_orders_empty_list(self):
        """Test affichage quand aucune commande"""
        new_user = User.objects.create_user('newuser', password='TestPass123!')
        self.client.login(username='newuser', password='TestPass123!')
        response = self.client.get('/my/orders/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['orders']), 0)

    def test_invoice_pdf_generates_correctly(self):
        """Test génération de facture PDF"""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(f'/orders/{self.order.id}/invoice.pdf')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn(f'invoice-{self.order.id}.pdf', response['Content-Disposition'])
        # Vérifier que le PDF contient des données
        self.assertGreater(len(response.content), 1000)  # PDF doit avoir une taille minimale

    def test_invoice_pdf_wrong_user(self):
        """Test accès facture PDF utilisateur non autorisé"""
        other_user = User.objects.create_user('other', password='TestPass123!')
        self.client.login(username='other', password='TestPass123!')
        response = self.client.get(f'/orders/{self.order.id}/invoice.pdf')
        self.assertEqual(response.status_code, 404)

    def test_invoice_pdf_nonexistent_order(self):
        """Test facture pour commande inexistante"""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get('/orders/99999/invoice.pdf')
        self.assertEqual(response.status_code, 404)

    def test_cart_add_redirect_get(self):
        """Test ajout panier via GET redirect"""
        response = self.client.get(f'/orders/cart/add/{self.offer1.id}/?qty=3&next=/offers/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/offers/')
        # Vérifier que l'article a été ajouté
        self.assertTrue('current_order_id' in self.client.session)

    def test_cart_add_redirect_invalid_offer(self):
        """Test ajout panier avec offre inexistante"""
        response = self.client.get('/orders/cart/add/99999/?qty=1')
        self.assertEqual(response.status_code, 404)

    def test_cart_add_redirect_invalid_qty(self):
        """Test ajout panier avec quantité invalide"""
        response = self.client.get(f'/orders/cart/add/{self.offer1.id}/?qty=invalid')
        self.assertEqual(response.status_code, 302)
        # Doit utiliser qty=1 par défaut

    def test_cart_update_redirect(self):
        """Test mise à jour panier via GET"""
        # D'abord ajouter un article
        self.client.get(f'/orders/cart/add/{self.offer1.id}/?qty=2')
        # Puis le modifier
        response = self.client.get(f'/orders/cart/update/{self.offer1.id}/?qty=5&next=/cart/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/cart/')

    def test_cart_update_redirect_missing_qty(self):
        """Test mise à jour panier sans qty"""
        response = self.client.get(f'/orders/cart/update/{self.offer1.id}/')
        self.assertEqual(response.status_code, 400)
        self.assertIn('qty requis', response.content.decode())

    def test_cart_update_redirect_zero_qty(self):
        """Test suppression article avec qty=0"""
        # Ajouter puis supprimer
        self.client.get(f'/orders/cart/add/{self.offer1.id}/?qty=1')
        response = self.client.get(f'/orders/cart/update/{self.offer1.id}/?qty=0')
        self.assertEqual(response.status_code, 302)

    def test_cart_clear_redirect(self):
        """Test vidage panier via GET"""
        # Ajouter des articles
        self.client.get(f'/orders/cart/add/{self.offer1.id}/?qty=1')
        self.client.get(f'/orders/cart/add/{self.offer2.id}/?qty=1')
        # Vider le panier
        response = self.client.get('/orders/cart/clear/?next=/home/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/home/')

    def test_checkout_redirect_requires_login(self):
        """Test que checkout nécessite une authentification"""
        response = self.client.get('/orders/checkout/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_checkout_redirect_empty_cart(self):
        """Test checkout avec panier vide"""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get('/orders/checkout/')
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('panier est vide' in str(m) for m in messages))

    def test_checkout_redirect_nonexistent_order(self):
        """Test checkout avec session corrompue"""
        self.client.login(username='testuser', password='TestPass123!')
        # Forcer un order_id invalide dans la session
        session = self.client.session
        session['current_order_id'] = 99999
        session.save()
        response = self.client.get('/orders/checkout/')
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('introuvable' in str(m) for m in messages))

    def test_checkout_redirect_success(self):
        """Test checkout réussi avec génération de tickets"""
        self.client.login(username='testuser', password='TestPass123!')
        # Ajouter des articles au panier via session
        session = self.client.session
        session['current_order_id'] = self.order.id
        session.save()
        
        # Mock la génération de tickets pour éviter les effets de bord
        from unittest.mock import patch
        with patch('tickets.models.Ticket.create_from') as mock_create:
            mock_create.return_value = Ticket(id=1, ticket_key='mock:key')
            response = self.client.get('/orders/checkout/')
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/my/tickets/')
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('réussi' in str(m) for m in messages))

    def test_checkout_redirect_adopts_guest_order(self):
        """Test adoption d'une commande invité lors du checkout"""
        guest_user = User.objects.create_user('guest', password='temp')
        guest_order = Order.objects.create(user=guest_user)
        OrderItem.objects.create(order=guest_order, offer=self.offer1, quantity=1)
        
        self.client.login(username='testuser', password='TestPass123!')
        session = self.client.session
        session['current_order_id'] = guest_order.id
        session.save()
        
        from unittest.mock import patch
        with patch('tickets.models.Ticket.create_from') as mock_create:
            mock_create.return_value = Ticket(id=1, ticket_key='mock:key')
            response = self.client.get('/orders/checkout/')
        
        self.assertEqual(response.status_code, 302)
        # Vérifier que la commande a été adoptée
        guest_order.refresh_from_db()
        self.assertEqual(guest_order.user, self.user)

    def test_cart_operations_with_inactive_offer(self):
        """Test opérations panier avec offre inactive"""
        inactive_offer = Offer.objects.create(
            name='Inactive', 
            offer_type='solo', 
            price_eur=30, 
            is_active=False
        )
        response = self.client.get(f'/orders/cart/add/{inactive_offer.id}/')
        self.assertEqual(response.status_code, 404)

    def test_session_modification_tracking(self):
        """Test que les modifications de session sont trackées"""
        initial_session_key = self.client.session.session_key
        self.client.get(f'/orders/cart/add/{self.offer1.id}/?qty=1')
        # Vérifier que la session a été modifiée
        self.assertTrue('current_order_id' in self.client.session)

    def test_pdf_with_multiple_pages(self):
        """Test génération PDF avec beaucoup d'articles (pagination)"""
        # Créer une commande avec beaucoup d'articles
        large_order = Order.objects.create(user=self.user)
        # Créer 50 articles pour forcer la pagination du PDF
        for i in range(50):
            OrderItem.objects.create(
                order=large_order, 
                offer=self.offer1, 
                quantity=1
            )
        
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(f'/orders/{large_order.id}/invoice.pdf')
        self.assertEqual(response.status_code, 200)
        # PDF multi-pages doit être plus volumineux
        self.assertGreater(len(response.content), 2000)
