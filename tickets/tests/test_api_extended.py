"""Tests étendus pour tickets/api.py - amélioration de la couverture"""

import tempfile
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from unittest.mock import patch
from offers.models import Offer
from orders.models import Order
from tickets.models import Ticket, checksum


@override_settings(
    MEDIA_ROOT=tempfile.gettempdir(),
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
)
class TicketsApiExtendedTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', 
            password='TestPass123!'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', 
            password='TestPass123!'
        )
        self.offer = Offer.objects.create(
            name='Solo Event', 
            offer_type='solo', 
            price_eur=50, 
            is_active=True
        )
        self.order = Order.objects.create(user=self.user)
        
        # Créer un ticket valide
        self.valid_ticket = Ticket.objects.create(
            user=self.user,
            order=self.order,
            offer=self.offer,
            ticket_key="user123:order456:offer789:abcd1234"
        )
        
        # Nettoyer le cache avant chaque test
        cache.clear()

    def test_verify_ticket_requires_authentication(self):
        """Test que l'API nécessite une authentification"""
        response = self.client.post('/api/tickets/verify/', {
            'ticket_key': self.valid_ticket.ticket_key
        })
        self.assertEqual(response.status_code, 403)

    def test_verify_ticket_missing_key(self):
        """Test vérification sans clé"""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post('/api/tickets/verify/', {})
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertIn('requise', data['error'])

    def test_verify_ticket_empty_key(self):
        """Test vérification avec clé vide"""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post('/api/tickets/verify/', {
            'ticket_key': '   '  # Clé vide après strip
        })
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertIn('requise', data['error'])

    def test_verify_ticket_too_long_key(self):
        """Test protection contre les clés trop longues (DoS)"""
        self.client.login(username='testuser', password='TestPass123!')
        long_key = 'x' * 201  # Plus de 200 caractères
        
        response = self.client.post('/api/tickets/verify/', {
            'ticket_key': long_key
        })
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertIn('trop longue', data['error'])

    def test_verify_ticket_invalid_format(self):
        """Test vérification avec format invalide (pas de ':')"""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post('/api/tickets/verify/', {
            'ticket_key': 'invalid_key_without_colon'
        })
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertIn('Format invalide', data['error'])

    def test_verify_ticket_invalid_checksum(self):
        """Test vérification avec checksum invalide"""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post('/api/tickets/verify/', {
            'ticket_key': 'raw_data:invalid_checksum'
        })
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertIn('Checksum invalide', data['error'])

    def test_verify_ticket_nonexistent(self):
        """Test vérification d'un ticket qui n'existe pas"""
        self.client.login(username='testuser', password='TestPass123!')
        
        # Créer une clé avec un checksum valide mais qui ne correspond à aucun ticket
        raw_data = 'nonexistent:ticket:key'
        valid_checksum = checksum(raw_data)
        fake_key = f"{raw_data}:{valid_checksum}"
        
        response = self.client.post('/api/tickets/verify/', {
            'ticket_key': fake_key
        })
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertIn('inconnu', data['error'])

    def test_verify_ticket_wrong_user(self):
        """Test vérification d'un ticket appartenant à un autre utilisateur"""
        self.client.login(username='otheruser', password='TestPass123!')
        response = self.client.post('/api/tickets/verify/', {
            'ticket_key': self.valid_ticket.ticket_key
        })
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertIn('non autorisé', data['error'])

    def test_verify_ticket_success(self):
        """Test vérification réussie"""
        self.client.login(username='testuser', password='TestPass123!')
        
        # S'assurer que verified_at est None au début
        self.assertIsNone(self.valid_ticket.verified_at)
        
        response = self.client.post('/api/tickets/verify/', {
            'ticket_key': self.valid_ticket.ticket_key
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['ticket_id'], self.valid_ticket.id)
        self.assertEqual(data['offer'], self.offer.name)
        self.assertIn('verified_at', data)
        
        # Vérifier que verified_at a été mis à jour
        self.valid_ticket.refresh_from_db()
        self.assertIsNotNone(self.valid_ticket.verified_at)

    def test_verify_ticket_caching_failed_attempts(self):
        """Test mise en cache des tentatives échouées"""
        self.client.login(username='testuser', password='TestPass123!')
        invalid_key = 'invalid:checksum'
        
        # Première tentative - calcule et met en cache
        response1 = self.client.post('/api/tickets/verify/', {
            'ticket_key': invalid_key
        })
        self.assertEqual(response1.status_code, 400)
        
        # Vérifier que c'est en cache
        cache_key = f"ticket_verify_{invalid_key[:20]}"
        cached_result = cache.get(cache_key)
        self.assertIsNotNone(cached_result)
        
        # Deuxième tentative - doit utiliser le cache
        response2 = self.client.post('/api/tickets/verify/', {
            'ticket_key': invalid_key
        })
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response1.json(), response2.json())

    def test_verify_ticket_caching_successful_verification(self):
        """Test mise en cache des vérifications réussies"""
        self.client.login(username='testuser', password='TestPass123!')
        
        # Première vérification
        response1 = self.client.post('/api/tickets/verify/', {
            'ticket_key': self.valid_ticket.ticket_key
        })
        self.assertEqual(response1.status_code, 200)
        
        # Vérifier la mise en cache
        cache_key = f"ticket_verify_{self.valid_ticket.ticket_key[:20]}"
        cached_result = cache.get(cache_key)
        self.assertIsNotNone(cached_result)
        
        # Deuxième vérification - doit utiliser le cache
        response2 = self.client.post('/api/tickets/verify/', {
            'ticket_key': self.valid_ticket.ticket_key
        })
        self.assertEqual(response2.status_code, 200)

    @patch('tickets.api.cache')
    def test_verify_ticket_cache_failure_fallback(self, mock_cache):
        """Test comportement quand le cache échoue"""
        # Simuler une erreur de cache
        mock_cache.get.side_effect = Exception("Cache error")
        mock_cache.set.side_effect = Exception("Cache error")
        
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post('/api/tickets/verify/', {
            'ticket_key': self.valid_ticket.ticket_key
        })
        
        # Doit quand même fonctionner même si le cache échoue
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['ok'])

    def test_verify_ticket_database_optimization(self):
        """Test optimisation des requêtes avec select_related"""
        self.client.login(username='testuser', password='TestPass123!')
        
        with self.assertNumQueries(2):  # 1 pour la vérification + 1 pour l'update
            response = self.client.post('/api/tickets/verify/', {
                'ticket_key': self.valid_ticket.ticket_key
            })
        
        self.assertEqual(response.status_code, 200)

    def test_verify_ticket_multiple_colons_in_key(self):
        """Test clé avec plusieurs ':' (utilise rsplit)"""
        self.client.login(username='testuser', password='TestPass123!')
        
        # Créer une clé avec plusieurs ':'
        complex_key = 'user:123:order:456:offer:789:checksum'
        response = self.client.post('/api/tickets/verify/', {
            'ticket_key': complex_key
        })
        
        # Doit traiter correctement avec rsplit(1)
        self.assertEqual(response.status_code, 400)  # Checksum invalide mais format OK

    def test_verify_ticket_concurrent_verification(self):
        """Test vérifications concurrentes du même ticket"""
        self.client.login(username='testuser', password='TestPass123!')
        
        # Simuler des vérifications concurrentes
        responses = []
        for _ in range(3):
            response = self.client.post('/api/tickets/verify/', {
                'ticket_key': self.valid_ticket.ticket_key
            })
            responses.append(response)
        
        # Toutes doivent réussir (cache ou DB)
        for response in responses:
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json()['ok'])

    def test_verify_ticket_already_verified_timestamp_update(self):
        """Test mise à jour du timestamp pour ticket déjà vérifié"""
        # Pré-définir un timestamp
        old_time = timezone.now() - timezone.timedelta(hours=1)
        self.valid_ticket.verified_at = old_time
        self.valid_ticket.save()
        
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post('/api/tickets/verify/', {
            'ticket_key': self.valid_ticket.ticket_key
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que le timestamp a été mis à jour
        self.valid_ticket.refresh_from_db()
        self.assertGreater(self.valid_ticket.verified_at, old_time)

    def test_verify_ticket_get_method_not_allowed(self):
        """Test que seul POST est accepté"""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get('/api/tickets/verify/')
        
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_verify_ticket_json_response_format(self):
        """Test format exact de la réponse JSON"""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post('/api/tickets/verify/', {
            'ticket_key': self.valid_ticket.ticket_key
        })
        
        data = response.json()
        
        # Vérifier tous les champs requis
        required_fields = ['ok', 'ticket_id', 'offer', 'verified_at']
        for field in required_fields:
            self.assertIn(field, data)
        
        # Vérifier les types
        self.assertIsInstance(data['ok'], bool)
        self.assertIsInstance(data['ticket_id'], int)
        self.assertIsInstance(data['offer'], str)
        self.assertIsInstance(data['verified_at'], str)

    def test_verify_ticket_edge_case_whitespace(self):
        """Test gestion des espaces dans la clé"""
        self.client.login(username='testuser', password='TestPass123!')
        
        # Clé avec espaces au début/fin
        key_with_spaces = f"  {self.valid_ticket.ticket_key}  "
        response = self.client.post('/api/tickets/verify/', {
            'ticket_key': key_with_spaces
        })
        
        # Doit fonctionner (strip() appliqué)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])