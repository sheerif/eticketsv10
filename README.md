# eTickets JO 2024 - Ma plateforme de billetterie

Salut ! C'est mon projet de fin de formation pour le Bachelor Développeur Python chez STUDI. J'ai développé une plateforme complète de vente de billets pour les JO 2024 avec Django.

## Demo en ligne

- **Site principal :** https://etickets-v10.fly.dev/
- **Administration :** https://etickets-v10.fly.dev/admin/ (admin / AdminPass123!)
- **Trello du projet :** https://trello.com/b/C0JIkk1g/jo-2024-studi-bloc-3-kanban

## À propos du projet

**Contexte académique :** 
- Formation : Bachelor Développeur d'application Python
- École : STUDI  
- Objectif : Projet d'examen bloc 3
- Statut : Déployé en production et fonctionnel

J'ai voulu créer quelque chose de complet qui ressemble à une vraie plateforme de billetterie. Le thème des JO 2024 m'a motivé à faire quelque chose de bien !

## Fonctionnalités développées

### Système de billetterie
- **Catalogue d'offres :** Événements Solo, Duo et Famille
- **Types de billets :** Athlétisme, Natation, Cyclisme, etc.
- **Pricing dynamique :** Calcul automatique des totaux
- **Design responsive :** Interface qui s'adapte à tous les écrans

### Gestion utilisateurs  
- **Inscription/Connexion :** Authentification sécurisée avec Django
- **Profils utilisateur :** Gestion des infos personnelles
- **Historique complet :** Suivi des commandes et billets
- **Sécurité :** Protection CSRF, sessions sécurisées

### Panier et commandes
- **Panier intelligent :** Ajout/suppression dynamique en AJAX
- **Panier persistant :** Conservation entre les sessions (même déconnecté)
- **Checkout simplifié :** Processus d'achat en une étape  
- **Paiement simulé :** Système de mock pour les tests
- **Confirmation instantanée :** Génération immédiate des billets

### Billets électroniques
- **Génération sécurisée :** Clés uniques avec SHA-256
- **QR codes authentiques :** Images PNG haute qualité
- **Téléchargement :** Billets accessibles hors ligne
- **Système de vérification :** Interface de scan pour l'entrée

### API REST moderne
- **Format JSON :** Communication avec Django REST Framework
- **AJAX :** Interactions dynamiques sans rechargement
- **Architecture moderne :** Séparation frontend/backend

## Installation et démarrage

### Prérequis
- Python 3.11+ obligatoire
- Environnement Windows, Mac ou Linux

### Installation rapide

```bash
# Vérifier Python
python --version

# Si problème PowerShell sur Windows
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# Cloner le repository
git clone https://github.com/sheerif/eticketsv10.git
cd eticketsv10

# Créer l'environnement virtuel
python -m venv .venv
# Windows
.\.venv\Scripts\Activate.ps1
# Mac/Linux
source .venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Configuration
cp .env.example .env

# Setup automatique (recommandé)
python scripts/setup.py

# OU setup manuel :
# python manage.py migrate
# python manage.py seed_offers  
# python scripts/create_superuser.py --default

# Démarrer le serveur
python manage.py runserver
```

### URLs importantes
- **Accueil :** http://127.0.0.1:8000/
- **Billets :** http://127.0.0.1:8000/offers/
- **Connexion :** http://127.0.0.1:8000/login/
- **Inscription :** http://127.0.0.1:8000/signup/
- **Administration :** http://127.0.0.1:8000/admin/
- **Scan tickets :** http://127.0.0.1:8000/scan/

## Configuration avancée

### Base de données
J'ai configuré le projet pour supporter plusieurs BDD selon l'environnement :

```bash
# SQLite (par défaut - développement)
# Aucune config nécessaire, utilise db.sqlite3 automatiquement

# PostgreSQL (production recommandé)  
DATABASE_URL=postgres://username:password@localhost:5432/etickets_db

# MySQL/MariaDB (si besoin)
DATABASE_URL=mysql://username:password@localhost:3306/etickets_db
```

### Variables d'environnement
Le fichier `.env` permet de tout configurer :

```bash
# Configuration de base
DJANGO_ENV=development          # ou production  
DJANGO_SECRET_KEY=change-me     # OBLIGATOIRE : clé unique
DEBUG=1                         # 1=True, 0=False

# Base de données  
DATABASE_URL=postgres://...     # si PostgreSQL

# Domaines et sécurité
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000

# Interface admin
ADMIN_URL=admin/                # URL personnalisée

# Médias et fichiers
# MEDIA_ROOT=                   # Dossier médias personnalisé
```

**Important :** Il faut absolument générer une clé secrète unique :
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Configuration Docker
J'ai aussi préparé un setup Docker complet pour ceux qui préfèrent :

```bash
# Copier la config Docker
cp .env.example .env.docker

# Lancer avec Docker
docker compose up --build

# Dans un autre terminal pour la DB
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_offers
docker compose exec web python manage.py createsuperuser
```

Le `docker-compose.yml` lance une stack complète :
- Application Django sur le port 8000
- PostgreSQL 16 en base de données  
- Volumes pour la persistance des données

## Tests et qualité

J'ai développé une suite de tests pour valider les fonctionnalités :

```bash
# Tests par module
python manage.py test accounts    # Authentification (100%)
python manage.py test offers     # Catalogue (100%) 
python manage.py test orders     # Commandes (100%)
python manage.py test tickets    # Billets (100%)
python manage.py test core       # Fonctions communes (100%)

# Tests étendus
python manage.py test accounts.tests.test_views_extended
python manage.py test orders.tests.test_views_extended
python manage.py test tickets.tests.test_api_extended

# Suite complète
python manage.py test --keepdb   # Plus rapide avec base persistante
```

**Résultats actuels :**
- 39 tests au total
- 100% de réussite après corrections
- Couverture globale : 85%+

### Analyse de couverture
```bash
# Installer coverage
pip install coverage

# Lancer les tests avec analyse
coverage run --source='.' manage.py test
coverage report -m --skip-covered
coverage html

# Ouvrir le rapport
start htmlcov\index.html
```

## Déploiement en production

### Fly.io (ma solution)
Le projet est déployé sur Fly.io avec cette config :
- **Runtime :** Python 3.12 + Gunicorn
- **Base de données :** PostgreSQL hébergé
- **Région :** CDG (Paris, France) 
- **HTTPS :** Certificat SSL automatique
- **Auto-scaling :** Machine qui s'arrête/démarre selon la demande

```bash
# Installation Fly CLI
iwr https://fly.io/install.ps1 -useb | iex   # Windows
# curl -L https://fly.io/install.sh | sh     # Mac/Linux

# Authentification
fly auth login

# Déploiement
fly deploy

# Commandes utiles  
fly status          # Statut de l'app
fly logs           # Logs temps réel
fly ssh console    # Accès serveur
fly secrets list   # Voir les variables
```

### Gestion des secrets
```bash
# Variables sensibles pour prod
fly secrets set DJANGO_SECRET_KEY="$(python -c '...')"
fly secrets set DJANGO_ENV=production
fly secrets set DEBUG=0
fly secrets set DATABASE_URL="postgres://..."
```

### Autres plateformes  
Le projet peut aussi être déployé sur Heroku, Railway, ou n'importe quel serveur VPS avec quelques adaptations de la config.

## Structure du projet

```
eticketsv10/
├── accounts/               # Gestion des utilisateurs
│   ├── models.py          # Modèles User étendus
│   ├── views.py           # Vues auth (login, signup)
│   ├── forms.py           # Formulaires d'inscription
│   └── templates/         # Templates auth
├── core/                  # Fonctionnalités communes  
│   ├── security.py        # Fonctions de sécurité
│   ├── utils.py           # Utilitaires partagés
│   └── mixins.py          # Mixins pour les vues
├── offers/                # Catalogue des offres
│   ├── models.py          # Modèle Offer
│   ├── views.py           # Vues catalogue
│   └── management/        # Commandes Django
├── orders/                # Gestion des commandes
│   ├── models.py          # Modèles Order, OrderItem  
│   ├── views.py           # Panier, checkout
│   ├── api.py             # API REST du panier
│   └── cart.py            # Logique panier
├── tickets/               # Billets électroniques
│   ├── models.py          # Modèle Ticket
│   ├── views.py           # Génération, téléchargement
│   ├── api.py             # API vérification
│   └── utils.py           # Génération QR codes
├── templates/             # Templates HTML
│   ├── base.html          # Template de base
│   ├── includes/          # Composants réutilisables
│   └── [app]/             # Templates par app
├── static/                # Fichiers statiques
│   ├── css/              # Feuilles de style
│   ├── js/               # JavaScript
│   └── images/           # Images du site
├── scripts/               # Scripts d'automatisation
│   ├── setup.py          # Configuration auto
│   └── create_superuser.py # Création admin
├── docker/                # Configuration Docker
│   └── entrypoint.sh     # Script de démarrage
├── requirements.txt       # Dépendances Python
├── docker-compose.yml     # Config Docker dev
├── fly.toml              # Config Fly.io
├── .env.example          # Variables d'env exemple
└── .gitignore            # Fichiers à ignorer
```

## API REST Documentation

L'application expose une API REST pour les interactions dynamiques :

### Endpoints du panier
```bash
# Récupérer le contenu du panier
GET /api/cart/
# Réponse : {"items": [...], "total": 100.0}

# Ajouter un produit  
POST /api/cart/add/
# Body : {"offer_id": 1, "qty": 2}
# Réponse : {"ok": true}

# Modifier une quantité
POST /api/cart/update/
# Body : {"offer_id": 1, "qty": 5}

# Vider le panier
POST /api/cart/clear/

# Finaliser la commande (authentification requise)
POST /api/cart/checkout/  
# Réponse : {"ok": true, "order_id": 42, "tickets": [101, 102]}
```

### Autres endpoints
```bash
# Liste des offres actives
GET /api/offers/

# Vérification d'un ticket (authentifié)
POST /api/tickets/verify/
# Body : {"ticket_key": "abc123:hash456"}

# Santé de l'application  
GET /health/
```

### Authentification
- **Sessions Django** pour l'auth standard
- **Protection CSRF** sur tous les POST/PUT/DELETE
- **Permissions** différenciées par endpoint

## Sécurité implémentée

### Mesures de protection
- **HTTPS forcé** en production avec redirection
- **HSTS** (HTTP Strict Transport Security)
- **Protection CSRF** sur tous les formulaires
- **Validation des mots de passe** Django par défaut
- **Admin sécurisé** avec URL personnalisable
- **Variables d'environnement** pour les secrets
- **Checksums SHA-256** pour les tickets

### Bonnes pratiques appliquées
- Secrets jamais commitées (fichier `.env` dans `.gitignore`)
- Clés différentes par environnement
- Mots de passe robustes obligatoires
- Variables sensibles dans les systèmes de secrets du cloud

## Difficultés rencontrées et solutions

### Gestion du panier pour utilisateurs non-connectés
**Problème :** Comment gérer un panier avant connexion ?
**Solution :** Utilisation des sessions Django qui persistent même déconnecté, avec adoption automatique du panier guest lors de la connexion.

### Génération sécurisée des tickets  
**Problème :** Éviter la contrefaçon des billets électroniques
**Solution :** Système de clés SHA-256 avec checksums impossibles à deviner

### Configuration multi-environnement
**Problème :** Même code pour dev (SQLite) et prod (PostgreSQL)
**Solution :** `dj-database-url` avec fallback automatique selon la variable `DATABASE_URL`

### Déploiement et fichiers statiques
**Problème :** CSS/JS pas chargés en production sur Fly.io
**Solution :** WhiteNoise configuré avec `WHITENOISE_USE_FINDERS=True`

### Tests et formats de dates
**Problème :** Tests échouaient à cause des formats de date
**Solution :** Harmonisation des templates avec format `d/m/Y H:i`

## Améliorations futures possibles

Si j'avais plus de temps pour ce projet, j'ajouterais :

### Fonctionnalités métier
- **Paiement réel** avec Stripe ou PayPal  
- **Notifications email** automatiques (confirmation, rappels)
- **Système de réductions** (codes promo, tarifs étudiants)
- **Plus de types de billets** (VIP, accès multiple, etc.)
- **Gestion des places** avec plan de salle

### Aspects techniques  
- **Cache Redis** pour les performances
- **Monitoring** avec Sentry pour les erreurs
- **Tests d'intégration** plus poussés  
- **API versioning** pour l'évolutivité
- **Interface admin** plus jolie avec django-admin-interface

### UX/UI
- **PWA** (Progressive Web App) pour mobile
- **Notifications push** 
- **Mode sombre** 
- **Multi-langue** français/anglais

## FAQ et dépannage

### Erreurs courantes

**Q: PowerShell bloque l'activation du venv**
```bash
R: Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Q: Le panier ne se met pas à jour dynamiquement**  
```bash  
R: Vérifiez que JavaScript est activé et que l'API /api/cart/ répond
```

**Q: Mes commandes restent "En attente"**
```bash
R: Le statut passe à "Payée" automatiquement quand des billets sont générés
```

**Q: Port 8000 déjà utilisé**
```bash  
R: python manage.py runserver 8080
```

### Génération de clé secrète
```bash
# Méthode 1: Django  
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Méthode 2: Python standard
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## Notes personnelles sur le développement

Ce projet a été un super challenge pour moi ! C'était ma première fois avec plusieurs technos :

### Ce que j'ai appris
- **Django REST Framework** : Première expérience avec les serializers et ViewSets
- **Sessions complexes** : Gestion panier persistant avec/sans auth
- **Déploiement cloud** : Premier déploiement sur Fly.io, j'ai galéré au début
- **Tests automatisés** : Écriture d'une vraie suite de tests complète
- **Architecture modulaire** : Séparation propre en apps Django

### Points dont je suis fier
- Le système de tickets sécurisés avec QR codes
- L'API REST qui marche nickel avec AJAX  
- Le déploiement en prod qui fonctionne
- La gestion du panier multi-utilisateurs
- Les 39 tests qui passent tous !

### Ce qui m'a pris le plus de temps
- Comprendre les sessions Django pour le panier
- Faire marcher les fichiers statiques en production  
- Débugger les problèmes de CSRF avec l'API
- Écrire tous les tests (mais ça valait le coup)

Le code n'est peut-être pas parfait partout, mais j'ai appris énormément et le résultat fonctionne bien. C'est déployé en production et ça marche !

---

**Support et contact :**
- Issues GitHub : https://github.com/sheerif/eticketsv10/issues
- Contact : Via la plateforme STUDI

**Licence :** MIT - Voir le fichier LICENSE pour les détails

**Développé avec ❤️ dans le cadre du Bachelor Développeur d'application Python chez STUDI**
