# 🏆 eTickets JO 2024 — Plateforme de Billetterie Olympique

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2.6-green.svg)](https://djangoproject.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.3-purple.svg)](https://getbootstrap.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**🌐 Démo en ligne** : [https://etickets-v10.fly.dev/](https://etickets-v10.fly.dev/)  
**📋 Gestion de projet** : [Trello Kanban](https://trello.com/b/C0JIkk1g/jo-2024-studi-bloc-3-kanban)  
**🎓 Contexte académique** : Projet d'examen **STUDI — Bachelor Développeur d'application Python**

---

## 📖 Table des matières

- [🎯 À propos du projet](#-à-propos-du-projet)
- [✨ Fonctionnalités](#-fonctionnalités)
- [🚀 Installation et démarrage](#-installation-et-démarrage)
- [🔧 Configuration avancée](#-configuration-avancée)
- [🧪 Tests et qualité](#-tests-et-qualité)
- [🌐 Déploiement](#-déploiement)
- [📁 Structure du projet](#-structure-du-projet)
- [🔐 Sécurité](#-sécurité)
- [🤔 FAQ et dépannage](#-faq-et-dépannage)

---

## 🎯 À propos du projet

**eTickets JO 2024** est une plateforme de billetterie numérique développée dans le cadre du **Bachelor Développeur d'application Python** chez **STUDI**. Cette application simule la vente et la gestion de billets pour les Jeux Olympiques de Paris 2024.

### 🎓 Contexte pédagogique
- **Formation** : Bachelor Développeur d'application Python
- **École** : STUDI
- **Objectif** : Projet d'examen démontrant la maîtrise de Django, des API REST, et du développement web moderne
- **Durée** : Bloc 3 du cursus
- **Évaluation** : Projet professionnel complet avec déploiement en production

### 🌟 Particularités du projet
- **Paiements simulés** : Aucune transaction réelle n'est effectuée
- **QR Codes authentiques** : Génération de tickets avec codes SHA-256
- **Design responsive** : Interface optimisée pour tous les écrans
- **Architecture moderne** : API REST, AJAX, Bootstrap 5

---

## ✨ Fonctionnalités

### 🎫 Gestion des billets
- **Catalogue d'offres** : Événements Solo, Duo et Famille
- **Panier intelligent** : Ajout/suppression dynamique via AJAX
- **Types de billets** : Athlétisme, Natation, Cyclisme, etc.
- **Pricing dynamique** : Calcul automatique des totaux

### 👥 Système utilisateur
- **Inscription/Connexion** : Authentification sécurisée Django
- **Profils utilisateur** : Gestion des informations personnelles  
- **Historique complet** : Suivi des commandes et billets
- **Sécurité avancée** : Protection CSRF, sessions sécurisées

### 🛒 Processus d'achat
- **Panier persistant** : Conservation entre les sessions
- **Checkout simplifié** : Processus d'achat en une étape
- **Paiement mock** : Simulation de paiement sécurisé
- **Confirmation instantanée** : Génération immédiate des billets

### 🎟️ E-tickets et QR codes
- **Génération sécurisée** : Clés uniques SHA-256
- **QR codes** : Images PNG haute qualité
- **Téléchargement** : Billets accessibles hors ligne
- **Vérification** : Système de scan pour l'entrée

---

## 🚀 Installation et démarrage

### ⚡ Installation rapide (Windows)

#### 1. **Prérequis**
```powershell
# Vérifier Python 3.11+
python --version

# Si problèmes d'exécution PowerShell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

#### 2. **Cloner et configurer**
```powershell
# Cloner le repository
git clone https://github.com/sheerif/eticketsv10.git
cd eticketsv10

# Créer l'environnement virtuel
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. **Configuration de base**
```powershell
# Copier la configuration d'exemple
Copy-Item .env.example .env

# Configuration automatique complète
python scripts/setup.py

# OU configuration manuelle :
# python manage.py migrate
# python manage.py seed_offers  
# python scripts/create_superuser.py --default
```

#### 4. **Lancement**
```powershell
# Démarrer le serveur
python manage.py runserver

# Le site est accessible sur http://127.0.0.1:8000/
```

### 🔗 URLs importantes après installation
- **🏠 Accueil** : http://127.0.0.1:8000/
- **🎫 Billets** : http://127.0.0.1:8000/offers/
- **🔐 Connexion** : http://127.0.0.1:8000/login/
- **📝 Inscription** : http://127.0.0.1:8000/signup/
- **👑 Administration** : http://127.0.0.1:8000/admin/
- **📱 Scan tickets** : http://127.0.0.1:8000/scan/

---

## 🔧 Configuration avancée

### 🗄️ Configuration de la base de données

#### 🔗 **Support multi-SGBD**
eTickets supporte plusieurs systèmes de base de données via `dj-database-url` :

```env
# 📂 SQLite (par défaut - développement)
# Aucune configuration nécessaire, utilise automatiquement db.sqlite3

# 🐘 PostgreSQL (recommandé pour production)
DATABASE_URL=postgres://username:password@localhost:5432/etickets_db

# 🐬 MySQL/MariaDB
DATABASE_URL=mysql://username:password@localhost:3306/etickets_db

# ☁️ PostgreSQL hébergé (Fly.io, Heroku, etc.)
DATABASE_URL=postgres://user:pass@host.region.postgres.database.com:5432/dbname?sslmode=require
```

#### ⚙️ **Configuration automatique**
```python
# Dans settings.py - Configuration intelligente
DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",  # Fallback SQLite
        conn_max_age=600,  # Pool de connexions (10min)
    )
}
```

#### 🚀 **Configuration par environnement**

**Développement local (SQLite)**
```powershell
# .env pour développement
DJANGO_ENV=development
DEBUG=1
# DATABASE_URL non définie = SQLite automatique
```

**Production (PostgreSQL)**  
```powershell
# Variables pour production
DJANGO_ENV=production
DEBUG=0  
DATABASE_URL=postgres://user:pass@host:5432/db?sslmode=require
```

### 🔐 Gestion des secrets et variables d'environnement

#### 📋 **Fichier .env complet**
Créez un fichier `.env` basé sur `.env.example` :

```env
# ============================================
# 🔧 CONFIGURATION DE BASE
# ============================================
DJANGO_ENV=development                    # development | staging | production
DJANGO_SECRET_KEY=change-me-please        # ⚠️  OBLIGATOIRE : Clé secrète unique
DEBUG=1                                   # 1=True, 0=False

# ============================================
# 🗄️ BASE DE DONNÉES  
# ============================================
# SQLite (par défaut si DATABASE_URL absent)
# DATABASE_URL=sqlite:///./db.sqlite3

# PostgreSQL (recommandé production)
# DATABASE_URL=postgres://user:pass@host:5432/dbname

# MySQL/MariaDB
# DATABASE_URL=mysql://user:pass@host:3306/dbname

# ============================================
# 🌐 DOMAINES ET SÉCURITÉ
# ============================================
ALLOWED_HOSTS=127.0.0.1,localhost        # Domaines autorisés
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000  # URLs de confiance CSRF

# ============================================
# 👑 INTERFACE D'ADMINISTRATION
# ============================================
ADMIN_URL=admin/                          # URL d'admin personnalisée

# ============================================
# 📁 MÉDIAS ET FICHIERS
# ============================================
# MEDIA_ROOT=                             # Dossier médias (défaut: BASE_DIR/media)

# ============================================
# ☁️ DÉPLOIEMENT (Fly.io)
# ============================================
# FLY_APP_NAME=etickets-v10               # Nom app Fly.io

# ============================================
# 📊 MONITORING ET LOGS
# ============================================
# LOG_LEVEL=INFO                          # DEBUG | INFO | WARNING | ERROR
```

#### 🔒 **Sécurité des secrets**

**⚠️ Secrets critiques à protéger :**
```env
# 🔑 Clé secrète Django (OBLIGATOIRE)
DJANGO_SECRET_KEY=votre-cle-secrete-longue-et-complexe-ici

# 🗄️ Chaîne de connexion DB (si PostgreSQL)
DATABASE_URL=postgres://user:password@host:5432/dbname
```

**🛡️ Bonnes pratiques :**
- ✅ **Jamais de commit** des fichiers `.env` (dans `.gitignore`)
- ✅ **Secrets différents** par environnement  
- ✅ **Clé SECRET_KEY** unique par projet (50+ caractères)
- ✅ **Mots de passe DB** robustes
- ✅ **Variables sensibles** dans le système de secrets du cloud

#### 🏗️ **Génération de clés sécurisées**
```powershell
# Générer une clé Django sécurisée
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Ou utiliser Python directement
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

#### ☁️ **Configuration en production**

**Fly.io**
```powershell
# Définir les secrets en production
fly secrets set DJANGO_SECRET_KEY="votre-cle-generee-ici"
fly secrets set DJANGO_ENV=production
fly secrets set DEBUG=0
fly secrets set ALLOWED_HOSTS=votre-app.fly.dev
fly secrets set DATABASE_URL="postgres://..."

# Lister les secrets définis
fly secrets list
```

**Variables publiques vs secrètes**
```powershell
# ✅ Variables publiques (dans fly.toml)
[env]
  DJANGO_ENV = "production"
  ADMIN_URL = "admin/"

# 🔒 Secrets (via fly secrets)
DJANGO_SECRET_KEY = "secret-key-here"
DATABASE_URL = "postgres://..."
```

### 🐳 Docker Compose (développement avec PostgreSQL)

```powershell
# Configuration Docker
Copy-Item .env.docker.example .env

# Lancer avec Docker
docker compose up --build

# Dans un autre terminal : migrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_offers
docker compose exec web python manage.py createsuperuser
```

---

## 🐳 Développement avec Docker

### 🚀 **Configuration Docker complète**

#### **1. Architecture Docker**
```yaml
# docker-compose.yml - Stack complète
services:
  web:          # Application Django
    build: .
    ports: ["8000:8000"]
    volumes: [".:/app"]          # Code synchronisé
    depends_on: [db]
    
  db:           # PostgreSQL 16
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: etickets_db
      POSTGRES_USER: etickets_user
      POSTGRES_PASSWORD: change-me
    volumes: [db_data:/var/lib/postgresql/data]
```

#### **2. Configuration environnement Docker**
Créez un fichier `.env.docker` pour Docker :

```env
# ============================================
# 🐳 CONFIGURATION DOCKER SPÉCIFIQUE  
# ============================================
DJANGO_ENV=development
DJANGO_SECRET_KEY=docker-dev-key-not-for-production
DEBUG=1

# 🗄️ Base de données PostgreSQL (conteneur)
DATABASE_URL=postgres://etickets_user:change-me@db:5432/etickets_db

# 🌐 Domaines Docker
ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000

# 👑 Super utilisateur automatique (optionnel)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@etickets.local  
DJANGO_SUPERUSER_PASSWORD=AdminPass123!

# 📦 Options de démarrage
COLLECTSTATIC=0                    # 0=désactivé en dev
```

#### **3. Commands Docker essentielles**

**🚀 Démarrage rapide**
```powershell
# Première installation
git clone https://github.com/sheerif/eticketsv10.git
cd eticketsv10

# Configuration Docker
Copy-Item .env.example .env.docker
# Éditer .env.docker avec les valeurs ci-dessus

# Démarrage complet
docker compose --env-file .env.docker up --build -d

# Vérifier les logs
docker compose logs -f web
```

**🔧 Gestion du cycle de vie**
```powershell
# Démarrer les services
docker compose up -d                    # Arrière-plan
docker compose up --build              # Rebuild + logs

# Arrêter les services  
docker compose down                     # Arrêt propre
docker compose down -v                  # + suppression volumes

# Redémarrer un service
docker compose restart web
docker compose restart db
```

**📊 Monitoring et debugging**
```powershell
# Logs en temps réel
docker compose logs -f                  # Tous services
docker compose logs -f web              # Application seulement
docker compose logs -f db               # PostgreSQL seulement

# Statistiques conteneurs
docker compose ps                       # État des services
docker compose top                      # Processus actifs

# Accès shell conteneur
docker compose exec web bash            # Shell application
docker compose exec db psql -U etickets_user -d etickets_db  # PostgreSQL
```

### 👑 **Gestion automatique du super utilisateur**

#### **🔄 Création automatique avec entrypoint**

Le projet utilise un script `docker/entrypoint.sh` intelligent qui :

1. **🔧 Exécute les migrations** automatiquement
2. **👤 Crée/met à jour le super utilisateur** si les variables sont définies
3. **🌱 Charge les données d'exemple** (seed_offers)
4. **🚀 Démarre l'application**

**Variables d'environnement pour super utilisateur :**
```env
# Dans .env.docker
DJANGO_SUPERUSER_USERNAME=admin              # Nom d'utilisateur admin
DJANGO_SUPERUSER_EMAIL=admin@etickets.local  # Email admin  
DJANGO_SUPERUSER_PASSWORD=AdminPass123!      # Mot de passe sécurisé
```

#### **📋 Script entrypoint automatisé**
```bash
#!/usr/bin/env sh
# docker/entrypoint.sh - Automatisation complète

echo "🔧 Running migrations..."
python manage.py migrate --noinput

# Création/mise à jour automatique du super utilisateur
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "👤 Ensuring superuser exists..."
  python - <<'PYCODE'
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "etickets.settings") 
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Récupération des variables d'environnement
username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com") 
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

# Création ou mise à jour
user, created = User.objects.get_or_create(
    username=username, 
    defaults={"email": email}
)
user.is_staff = True
user.is_superuser = True  
user.set_password(password)
user.save()

print(f"✅ Admin: {username} {'(created)' if created else '(updated)'}")
PYCODE
fi

echo "🌱 Seeding offers..."
python manage.py seed_offers || true

echo "🚀 Starting application..."
exec "$@"
```

#### **🔧 Utilisation manuelle du super utilisateur**
```powershell
# Méthode 1: Variables d'environnement (recommandée)
# Définir dans .env.docker puis redémarrer

# Méthode 2: Création manuelle dans le conteneur
docker compose exec web python manage.py createsuperuser

# Méthode 3: Script Python personnalisé
docker compose exec web python - <<'PYCODE'
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "etickets.settings")
django.setup()

from django.contrib.auth.models import User
user = User.objects.create_superuser(
    username='admin',
    email='admin@local.dev', 
    password='SecurePass123!'
)
print(f"✅ Superuser created: {user.username}")
PYCODE
```

### 🔒 **Sécurité Docker en production**

#### **⚠️ Variables sensibles**
```env
# ❌ NE JAMAIS utiliser en production
DJANGO_SUPERUSER_PASSWORD=AdminPass123!

# ✅ Utiliser les secrets Docker/Kubernetes
# Ou variables d'environnement sécurisées du cloud
```

#### **🛡️ Bonnes pratiques**
- **✅ Secrets externes** : Utiliser les systèmes de secrets (Kubernetes, Docker Swarm)
- **✅ Mots de passe robustes** : Minimum 12 caractères, complexité élevée
- **✅ Rotation régulière** : Changer les mots de passe administrateur
- **✅ Principe moindre privilège** : Créer des utilisateurs spécifiques par besoin

### 🚀 **Production avec Docker**

#### **🏗️ Image de production optimisée**
```dockerfile
# Dockerfile - Multi-stage optimisé
FROM python:3.12-slim as base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt gunicorn

# Application
COPY . .
EXPOSE 8000

# Production command
CMD ["gunicorn", "etickets.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### **☁️ Déploiement production**
```powershell
# Build image production
docker build -t etickets-prod .

# Run avec variables sécurisées
docker run -d \
  -p 8000:8000 \
  -e DJANGO_ENV=production \
  -e DEBUG=0 \
  -e DJANGO_SECRET_KEY="production-secret-key" \
  -e DATABASE_URL="postgres://..." \
  etickets-prod
```

---

## 🧪 Tests et qualité

### 🔍 Suite de tests complète

Le projet dispose d'une **suite de tests exhaustive** couvrant tous les aspects critiques :

#### 📋 **Tests par catégorie**
```powershell
# 🧪 Tests unitaires standard
python manage.py test accounts      # Authentification, inscription
python manage.py test offers       # Catalogue des offres  
python manage.py test orders       # Commandes et facturation
python manage.py test tickets      # Billets électroniques
python manage.py test core         # Fonctions communes

# 🚀 Tests étendus (nouvellement ajoutés)
python manage.py test accounts.tests.test_views_extended    # Vues d'authentification
python manage.py test orders.tests.test_views_extended     # Vues de commandes/panier
python manage.py test tickets.tests.test_api_extended      # API de vérification
python manage.py test core.tests.test_security            # Fonctions de sécurité
python manage.py test tests.test_e2e_integration          # Tests d'intégration E2E
python manage.py test tests.test_edge_cases               # Cas d'erreur et limites
```

#### 🎯 **Types de tests inclus**
- **Tests des vues** : Rendu, redirections, authentification, permissions
- **Tests d'API** : Réponses JSON, validation, cache, rate limiting  
- **Tests de sécurité** : Protection CSRF, XSS, injection SQL, middleware
- **Tests E2E** : Workflows complets utilisateur (inscription → achat → ticket)
- **Tests edge cases** : Gestion d'erreurs, données corrompues, limites système
- **Tests de performance** : Montée en charge, concurrence, optimisations

### 📊 Couverture de code

```powershell
# Installer coverage (si pas déjà fait)
pip install coverage

# Exécuter TOUS les tests avec couverture
coverage run --source='.' manage.py test

# Rapport en console avec détails
coverage report -m --skip-covered

# Rapport HTML interactif
coverage html

# Ouvrir le rapport dans le navigateur
start htmlcov\index.html  # Windows
```

#### 📈 **Objectifs de couverture**
- **Couverture globale** : 85%+ (améliorée depuis 58%)
- **Vues critiques** : 90%+ (orders/views.py, accounts/views.py)  
- **APIs** : 95%+ (tickets/api.py, core APIs)
- **Fonctions de sécurité** : 100% (core/security.py)

### 🔧 **Configuration des tests**

#### Variables d'environnement pour les tests
```env
# Dans .env ou pour les tests
DJANGO_SETTINGS_MODULE=etickets.settings
SECRET_KEY=test-key-not-for-production
DEBUG=1
```

#### Tests en parallèle (pour accélérer)
```powershell
# Exécution parallèle (plus rapide)
python manage.py test --parallel

# Tests spécifiques avec verbosité
python manage.py test tests.test_e2e_integration -v 2

# Tests sans création de base
python manage.py test --keepdb
```

### 🐛 **Tests de régression**

```powershell
# Avant chaque commit - tests critiques
python manage.py test accounts.tests.test_views_extended
python manage.py test orders.tests.test_cart_checkout  
python manage.py test tickets.tests.test_api_extended

# Avant déploiement - suite complète
coverage run --source='.' manage.py test
coverage report --fail-under=80  # Échoue si <80% couverture
```

### 📋 **Checklist qualité**

Avant chaque release :
- [ ] ✅ Tous les tests passent : `python manage.py test`
- [ ] 📊 Couverture ≥80% : `coverage report --fail-under=80`
- [ ] 🔒 Tests de sécurité OK : `python manage.py test core.tests.test_security`
- [ ] 🚀 Tests E2E fonctionnels : `python manage.py test tests.test_e2e_integration`
- [ ] ⚡ Pas de régression performance
- [ ] 🧪 Edge cases couverts : `python manage.py test tests.test_edge_cases`

---

## 🌐 Déploiement

### ☁️ Déploiement Fly.io (recommandé)

```powershell
# Installation Fly CLI (Windows)
iwr https://fly.io/install.ps1 -useb | iex

# Authentification
fly auth login

# Initialisation (si premier déploiement)
fly launch

# Configuration des secrets
fly secrets set DJANGO_SECRET_KEY="votre-clé-secrète"
fly secrets set DJANGO_ENV=production
fly secrets set DEBUG=0
fly secrets set ALLOWED_HOSTS=etickets-v10.fly.dev

# Déploiement
fly deploy

# Migrations en production
fly ssh console -C "python manage.py migrate"
fly ssh console -C "python manage.py seed_offers"
```

---

## 🚀 API REST et Endpoints

### 📋 **Architecture API**

eTickets expose une **API REST moderne** avec authentification, validation et optimisations performance :

- **Format** : JSON avec Django REST Framework
- **Authentification** : Session Django + CSRF protection  
- **Permissions** : Différenciées par endpoint
- **Performance** : Cache Redis, requêtes optimisées
- **Validation** : Sanitisation des inputs, rate limiting

### 🛒 **API Panier (Cart)**

#### `GET /api/cart/` - Résumé du panier
```bash
# Récupérer le contenu du panier actuel
curl -X GET http://127.0.0.1:8000/api/cart/
```

**Réponse** :
```json
{
  "items": [
    {
      "offer_id": 1,
      "name": "Ticket Solo - Athlétisme",
      "price": 50.0,
      "qty": 2,
      "line_total": 100.0
    }
  ],
  "total": 100.0
}
```

#### `POST /api/cart/add/` - Ajouter au panier  
```bash
# Ajouter 3 billets de l'offre ID 1
curl -X POST http://127.0.0.1:8000/api/cart/add/ \
  -H "Content-Type: application/json" \
  -d '{"offer_id": 1, "qty": 3}'
```

**Paramètres** :
- `offer_id` (int, requis) : ID de l'offre
- `qty` (int, optionnel) : Quantité (défaut: 1)

**Réponse** :
```json
{"ok": true, "order_id": 42}
```

#### `POST /api/cart/update/` - Modifier quantité
```bash
# Changer la quantité à 5 pour l'offre ID 1
curl -X POST http://127.0.0.1:8000/api/cart/update/ \
  -H "Content-Type: application/json" \
  -d '{"offer_id": 1, "qty": 5}'
```

#### `POST /api/cart/clear/` - Vider le panier
```bash
# Vider complètement le panier
curl -X POST http://127.0.0.1:8000/api/cart/clear/
```

#### `POST /api/cart/checkout/` - Finaliser commande ⚡
```bash
# Convertir panier en billets (authentifié requis)
curl -X POST http://127.0.0.1:8000/api/cart/checkout/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token"
```

**Authentification** : 🔒 Utilisateur connecté requis

**Réponse succès** :
```json
{
  "ok": true,
  "order_id": 42,
  "tickets": [101, 102, 103]  // IDs des billets créés
}
```

**Réponse erreur** :
```json
{
  "ok": false,
  "error": "Panier vide"
}
```

### 🎫 **API Offres**

#### `GET /api/offers/` - Liste des offres
```bash
# Récupérer toutes les offres actives
curl -X GET http://127.0.0.1:8000/api/offers/
```

**Réponse** :
```json
[
  {
    "id": 1,
    "name": "Ticket Solo - Athlétisme",
    "offer_type": "solo",
    "price_eur": 50.0,
    "is_active": true
  },
  {
    "id": 2,
    "name": "Ticket Duo - Natation",
    "offer_type": "duo", 
    "price_eur": 85.0,
    "is_active": true
  }
]
```

### 🎟️ **API Vérification Tickets**

#### `POST /api/tickets/verify/` - Vérifier un ticket ⚡
```bash
# Vérifier la validité d'un ticket par sa clé
curl -X POST http://127.0.0.1:8000/api/tickets/verify/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{"ticket_key": "abc123:hash456"}'
```

**Authentification** : 🔒 Utilisateur connecté requis  
**Cache** : Résultats mis en cache 5 min (succès) / 1 min (erreurs)

**Paramètres** :
- `ticket_key` (string, requis) : Clé complète du ticket avec checksum

**Réponse succès** :
```json
{
  "ok": true,
  "ticket_id": 101,
  "offer": "Ticket Solo - Athlétisme", 
  "verified_at": "2025-09-20T14:30:00Z"
}
```

**Réponses d'erreur** :
```json
// Clé invalide
{"ok": false, "error": "Format invalide"}

// Checksum incorrect  
{"ok": false, "error": "Checksum invalide"}

// Ticket inexistant
{"ok": false, "error": "Ticket inconnu ou non autorisé"}
```

### ❤️ **API System Health**

#### `GET /health/` - Status du système
```bash
# Vérifier le statut de l'application
curl -X GET http://127.0.0.1:8000/health/
```

**Réponse** :
```json
{
  "status": "ok",
  "time": "2025-09-20T14:30:00Z"
}
```

### 🔧 **Utilisation JavaScript (Frontend)**

#### Exemple d'intégration panier
```javascript
// Ajouter au panier via AJAX
async function addToCart(offerId, quantity = 1) {
  const response = await fetch('/api/cart/add/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(), // Protection CSRF
    },
    body: JSON.stringify({
      offer_id: offerId,
      qty: quantity
    })
  });
  
  const result = await response.json();
  if (result.ok) {
    updateCartDisplay(); // Mettre à jour l'affichage
  }
}

// Récupérer le panier
async function getCart() {
  const response = await fetch('/api/cart/');
  return await response.json();
}

// Finaliser la commande
async function checkout() {
  const response = await fetch('/api/cart/checkout/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    }
  });
  
  const result = await response.json();
  if (result.ok) {
    window.location.href = `/my/orders/${result.order_id}/`;
  } else {
    alert(result.error);
  }
}
```

### 🔒 **Sécurité et Authentification**

#### **Gestion des sessions**
- **Utilisateurs anonymes** : Sessions temporaires automatiques
- **Utilisateurs connectés** : Adoption automatique du panier guest
- **Protection CSRF** : Tokens obligatoires sur POST/PUT/DELETE

#### **Validation des données**
- **Sanitisation** : Tous les inputs validés et nettoyés
- **Rate limiting** : Protection contre le spam d'API  
- **Taille des données** : Limites pour éviter les DoS
- **Checksums** : Vérification d'intégrité des tickets

#### **Permissions par endpoint**
| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /api/offers/` | 🌐 Public | Liste des offres |
| `GET /api/cart/` | 🌐 Public | Consultation panier |
| `POST /api/cart/*` | 🌐 Public | Gestion panier |
| `POST /api/cart/checkout/` | 🔒 Auth | Finalisation uniquement connecté |
| `POST /api/tickets/verify/` | 🔒 Auth | Vérification tickets |
| `GET /health/` | 🌐 Public | Monitoring système |

---

## 📁 Structure du projet

```
eticketsv10/
├── 📁 accounts/              # Gestion des utilisateurs
├── 📁 core/                  # Fonctionnalités communes
├── 📁 offers/                # Catalogue des offres
├── 📁 orders/                # Gestion des commandes
├── 📁 tickets/               # Billets électroniques
├── 📁 templates/             # Templates HTML
├── 📁 static/                # Fichiers statiques
├── 📄 requirements.txt       # Dépendances Python
├── 📄 docker-compose.yml     # Configuration Docker dev
└── 📄 .env.example           # Variables d'environnement
```

---

## 🔐 Sécurité

### 🛡️ Mesures implémentées
- **🔒 HTTPS forcé** : Redirection automatique en production
- **🛡️ HSTS** : HTTP Strict Transport Security
- **🚫 Protection CSRF** : Tokens sur tous les formulaires
- **🔑 Mots de passe** : Validation Django par défaut
- **🎯 Admin sécurisé** : URL personnalisable
- **📊 Variables d'environnement** : Secrets externalisés

---

## 🤔 FAQ et dépannage

### ❓ Questions fréquentes

**Q: PowerShell bloque l'activation du venv**  
R: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

**Q: Le panier ne se met pas à jour**  
R: Vérifiez que JavaScript est activé et que l'API `/api/cart/` répond.

**Q: "En attente" dans mes commandes**  
R: Le statut "Payée" s'affiche quand des billets sont générés.

**Q: Port 8000 déjà utilisé**  
R: `python manage.py runserver 8080`

### 📞 Support
- **🐛 Issues** : [GitHub Issues](https://github.com/sheerif/eticketsv10/issues)
- **📧 Contact** : Via la plateforme STUDI

---

## 📄 License

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- **🎓 STUDI** : Formation et accompagnement pédagogique
- **🐍 Django** : Framework web robuste et sécurisé  
- **🎨 Bootstrap** : Framework CSS moderne et responsive
- **☁️ Fly.io** : Plateforme de déploiement simple et efficace
- **🏆 CIO Paris 2024** : Inspiration pour le thème olympique

---

*Développé avec ❤️ dans le cadre du Bachelor Développeur d'application Python chez STUDI*