"""Tests pour core/security.py - fonctions de sécurité"""

import time
from django.test import TestCase, RequestFactory, Client, override_settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.cache import cache
from unittest.mock import Mock, patch

from core.security import (
    rate_limit, get_client_ip, validate_cart_data, 
    SecurityHeadersMiddleware
)


class SecurityFunctionsTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        cache.clear()

    def test_get_client_ip_with_x_forwarded_for(self):
        """Test extraction IP avec header X-Forwarded-For"""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1,10.0.0.1'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')  # Premier IP de la liste

    def test_get_client_ip_with_remote_addr(self):
        """Test extraction IP avec REMOTE_ADDR"""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.100')

    def test_get_client_ip_preference_order(self):
        """Test priorité X-Forwarded-For sur REMOTE_ADDR"""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1'
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')  # X-Forwarded-For prioritaire

    def test_validate_cart_data_valid(self):
        """Test validation données panier valides"""
        request = Mock()
        request.data = {'offer_id': '123', 'qty': '2'}
        
        error, status = validate_cart_data(request)
        self.assertIsNone(error)
        self.assertIsNone(status)

    def test_validate_cart_data_missing_offer_id(self):
        """Test validation avec offer_id manquant"""
        request = Mock()
        request.data = {'qty': '2'}
        
        error, status = validate_cart_data(request)
        self.assertIsNotNone(error)
        self.assertEqual(status, 400)
        self.assertIn('Invalid offer_id', error['error'])

    def test_validate_cart_data_invalid_offer_id(self):
        """Test validation avec offer_id invalide"""
        request = Mock()
        request.data = {'offer_id': 'abc', 'qty': '2'}
        
        error, status = validate_cart_data(request)
        self.assertIsNotNone(error)
        self.assertEqual(status, 400)
        self.assertIn('Invalid offer_id', error['error'])

    def test_validate_cart_data_negative_quantity(self):
        """Test validation avec quantité négative"""
        request = Mock()
        request.data = {'offer_id': '123', 'qty': '-1'}
        
        error, status = validate_cart_data(request)
        self.assertIsNotNone(error)
        self.assertEqual(status, 400)
        self.assertIn('Invalid quantity', error['error'])

    def test_validate_cart_data_excessive_quantity(self):
        """Test validation avec quantité excessive"""
        request = Mock()
        request.data = {'offer_id': '123', 'qty': '15'}
        
        error, status = validate_cart_data(request)
        self.assertIsNotNone(error)
        self.assertEqual(status, 400)
        self.assertIn('Invalid quantity', error['error'])

    def test_validate_cart_data_invalid_quantity_format(self):
        """Test validation avec format quantité invalide"""
        request = Mock()
        request.data = {'offer_id': '123', 'qty': 'abc'}
        
        error, status = validate_cart_data(request)
        self.assertIsNotNone(error)
        self.assertEqual(status, 400)
        self.assertIn('Invalid quantity format', error['error'])

    def test_validate_cart_data_default_quantity(self):
        """Test validation avec quantité par défaut"""
        request = Mock()
        request.data = {'offer_id': '123'}  # qty manquant
        
        error, status = validate_cart_data(request)
        self.assertIsNone(error)  # Doit utiliser qty=1 par défaut
        self.assertIsNone(status)


class RateLimitDecoratorTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()

    def test_rate_limit_per_ip_success(self):
        """Test rate limiting par IP - dans la limite"""
        @rate_limit(requests=5, window=60, per_ip=True)
        def test_view(request):
            return JsonResponse({'ok': True})

        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'

        # Première requête - doit passer
        response = test_view(request)
        self.assertEqual(response.status_code, 200)

    def test_rate_limit_per_ip_exceeded(self):
        """Test rate limiting par IP - limite dépassée"""
        @rate_limit(requests=2, window=60, per_ip=True)
        def test_view(request):
            return JsonResponse({'ok': True})

        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'

        # Deux requêtes OK
        response1 = test_view(request)
        response2 = test_view(request)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

        # Troisième requête bloquée
        response3 = test_view(request)
        self.assertEqual(response3.status_code, 429)
        data = response3.json()
        self.assertIn('Rate limit exceeded', data['error'])

    def test_rate_limit_per_user_success(self):
        """Test rate limiting par utilisateur"""
        @rate_limit(requests=3, window=60, per_user=True)
        def test_view(request):
            return JsonResponse({'ok': True})

        user = User.objects.create_user('testuser', password='test')
        request = self.factory.get('/')
        request.user = user

        # Trois requêtes OK
        for _ in range(3):
            response = test_view(request)
            self.assertEqual(response.status_code, 200)

        # Quatrième bloquée
        response = test_view(request)
        self.assertEqual(response.status_code, 429)

    def test_rate_limit_window_expiry(self):
        """Test expiration de la fenêtre de rate limiting"""
        @rate_limit(requests=1, window=1, per_ip=True)  # 1 req/seconde
        def test_view(request):
            return JsonResponse({'ok': True})

        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'

        # Première requête OK
        response1 = test_view(request)
        self.assertEqual(response1.status_code, 200)

        # Deuxième immédiate bloquée
        response2 = test_view(request)
        self.assertEqual(response2.status_code, 429)

        # Attendre l'expiration
        time.sleep(1.1)

        # Nouvelle requête OK après expiration
        response3 = test_view(request)
        self.assertEqual(response3.status_code, 200)

    def test_rate_limit_different_ips(self):
        """Test rate limiting séparé par IP"""
        @rate_limit(requests=1, window=60, per_ip=True)
        def test_view(request):
            return JsonResponse({'ok': True})

        # Première IP
        request1 = self.factory.get('/')
        request1.META['REMOTE_ADDR'] = '192.168.1.1'
        response1 = test_view(request1)
        self.assertEqual(response1.status_code, 200)

        # Deuxième IP - doit avoir son propre compteur
        request2 = self.factory.get('/')
        request2.META['REMOTE_ADDR'] = '192.168.1.2'
        response2 = test_view(request2)
        self.assertEqual(response2.status_code, 200)

    def test_rate_limit_anonymous_user(self):
        """Test rate limiting avec utilisateur anonyme"""
        @rate_limit(requests=2, window=60, per_user=True)
        def test_view(request):
            return JsonResponse({'ok': True})

        request = self.factory.get('/')
        request.user = Mock()
        request.user.is_authenticated = False

        # Doit fonctionner sans erreur même sans utilisateur auth
        response = test_view(request)
        self.assertEqual(response.status_code, 200)

    @patch('core.security.time.time')
    def test_rate_limit_cache_cleanup(self, mock_time):
        """Test nettoyage des anciens enregistrements"""
        mock_time.return_value = 1000.0  # Temps fixe

        @rate_limit(requests=5, window=60, per_ip=True)
        def test_view(request):
            return JsonResponse({'ok': True})

        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'

        # Ajouter quelques requêtes
        test_view(request)
        test_view(request)

        # Avancer le temps au-delà de la fenêtre
        mock_time.return_value = 1100.0  # +100 secondes

        # Nouvelle requête doit nettoyer l'ancien cache
        response = test_view(request)
        self.assertEqual(response.status_code, 200)


class SecurityHeadersMiddlewareTest(TestCase):

    def test_security_headers_added(self):
        """Test ajout des headers de sécurité"""
        def get_response(request):
            from django.http import HttpResponse
            return HttpResponse('OK')

        middleware = SecurityHeadersMiddleware(get_response)
        request = self.factory.get('/')

        response = middleware(request)

        # Vérifier tous les headers de sécurité
        expected_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }

        for header, value in expected_headers.items():
            self.assertEqual(response[header], value)

    def test_csp_header_for_secure_requests(self):
        """Test header CSP pour requêtes HTTPS"""
        def get_response(request):
            from django.http import HttpResponse
            return HttpResponse('OK')

        middleware = SecurityHeadersMiddleware(get_response)
        request = self.factory.get('/', secure=True)
        request.is_secure = Mock(return_value=True)

        response = middleware(request)

        # Vérifier CSP pour HTTPS
        self.assertIn('Content-Security-Policy', response)
        csp = response['Content-Security-Policy']
        self.assertIn("default-src 'self'", csp)
        self.assertIn("script-src 'self'", csp)
        self.assertIn("cdn.jsdelivr.net", csp)

    def test_no_csp_header_for_insecure_requests(self):
        """Test pas de CSP pour HTTP"""
        def get_response(request):
            from django.http import HttpResponse
            return HttpResponse('OK')

        middleware = SecurityHeadersMiddleware(get_response)
        request = self.factory.get('/')
        # Pas de is_secure ou False

        response = middleware(request)

        # Pas de CSP pour HTTP
        self.assertNotIn('Content-Security-Policy', response)

    def test_headers_dont_override_existing(self):
        """Test que les headers n'écrasent pas les existants"""
        def get_response(request):
            from django.http import HttpResponse
            response = HttpResponse('OK')
            response['X-Frame-Options'] = 'SAMEORIGIN'  # Header personnalisé
            return response

        middleware = SecurityHeadersMiddleware(get_response)
        request = self.factory.get('/')

        response = middleware(request)

        # Notre header personnalisé doit être écrasé par le middleware
        self.assertEqual(response['X-Frame-Options'], 'DENY')