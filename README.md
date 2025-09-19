# eTickets JO — etickets-v10   Démo : https://etickets-v10.fly.dev/

## 1. Fonctionnalités
- Offres (solo, duo, familiale) avec ajout au panier
- Compte utilisateur (signup/login)
- Paiement **mock** → génération d'**e-ticket** (QR code) basé sur deux clés (user + achat, hash SHA-256)
- Vérification/scanner du ticket
- Espace **Mes billets**
- Admin : gestion des offres, rapport de ventes (basique)

## 2. Lancer en local (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Base SQLite par défaut (sinon voir .env.example pour DATABASE_URL)
python manage.py migrate
python manage.py seed_offers
python manage.py runserver
```
- Accueil/offres : http://127.0.0.1:8000/offers/
- Login : /login/ — Signup : /signup/
- Scan : /scan/ — Mes billets : /my/tickets/

> Variables : copie `.env.example` en `.env` si tu veux surcharger `DJANGO_SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`, `FLY_APP_NAME`…

## 3. Tests & Couverture
=======

# eTickets JO — etickets-v10  
**Démo** : https://etickets-v10.fly.dev/

> Projet d’examen **STUDI — Bachelor Développeur d'application Python**  
> Front refondu **Bootstrap 5** (responsive) · QR affichés dans *Mes tickets* · Facture PDF en nouvel onglet

---


## Liens utiles
- **Admin (local)** : http://127.0.0.1:8000/admin/ (connexion avec le super utilisateur)
- **Site (démo)** : https://etickets-v10.fly.dev/
- **Trello** : https://trello.com/b/C0JIkk1g/jo-2024-studi-bloc-3-kanban



## 1) Fonctionnalités
- Catalogue d’**offres** (solo, duo, familiale) + **ajout au panier**
- **Compte utilisateur** (signup/login)
- **Paiement mock** → génération d’**e‑tickets** (QR code) basés sur 2 clés et un hash **SHA‑256** :
  - `user_key` (créée à l’inscription)
  - `purchase_key` (générée à l’achat)
  - `ticket_key = sha256(user_key + purchase_key)`
- **Mes billets** : listing, **clé affichée**, **QR cliquable**
- **Vérification / Scan** : via **POST `/api/tickets/verify/`** (auth requise)
- **Mes commandes** : lignes + total, **facture PDF** (`/orders/<id>/invoice.pdf`) ouverte **dans un nouvel onglet**
- **Admin** : gestion des offres, mini rapport des ventes

---

## 2) Lancer en local (Windows PowerShell)
```powershell
# 0) (si PowerShell bloque les scripts)
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# 1) Environnement
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2) Base SQLite par défaut (sinon voir .env.example pour DATABASE_URL)
python manage.py migrate
python manage.py seed_offers

# 3) Run
python manage.py runserver
```
**Raccourci CMD (sans changer la stratégie PS)** :
```cmd
.\.venv\Scripts\activate.bat
```

**URLs utiles**
- Offres : http://127.0.0.1:8000/offers/
- Login : `/login/` · Signup : `/signup/`
- Mes commandes : `/my/orders/`
- Mes billets : `/my/tickets/`
- Scan : `/scan/` (nécessite d’être connecté)
- Admin : `/admin/` (utilise le super utilisateur)

> Variables : copie **`.env.example`** en **`.env`** pour surcharger `DJANGO_SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`, `FLY_APP_NAME`…

---


## 3) Tests & Couverture

>>>>>>> 9ea62a1 (feat: import projet (refonte front, sécurité env, README, tests))
```powershell
# Tests Django
python manage.py test

# Couverture (rapide)
coverage run manage.py test
coverage report -m
coverage html  # ouvre htmlcov/index.html
```
<<<<<<< HEAD
Périmètre tests ajouté : modèles (Offer, Order), vue liste des offres.

## 4. Branches Git (workflow simple)
- `main` : prod (stable)
- `develop` : intégration (features)
```powershell
git checkout -b develop
git push -u origin develop
# Travail -> commit -> PR vers main
```

## 5. Déploiement Fly.io (PostgreSQL)
```powershell
fly launch  # génère fly.toml
# Secrets
fly secrets set DJANGO_SECRET_KEY=... ALLOWED_HOSTS=etickets-v10.fly.dev DEBUG=0
# Base Postgres (si pas encore)
fly postgres create
fly postgres attach
# Déploiement
fly deploy
# Migrations en prod (si release_command non configurée)
fly ssh console -C "python manage.py migrate"
=======


## 3) Front (refonte)
- **Bootstrap 5** via CDN + `static/css/theme.css`
- Navbar avec **URLs nommées** Django (`index`, `login`, `my_orders`, `my_tickets`, `scan_page`)
- **Panier** côté Offres : lecture du résumé via **GET `/api/cart/`**
- **Facture PDF** : lien avec `target="_blank"` (meilleur support mobile)
- Page **/scan/** : formulaire qui **POST** sur `/api/tickets/verify/` (CSRF inclus)  
  - Déconnecté → message + redirection automatique vers `/login/?next=/scan/`

---

## 4) API (extraits)
```
GET  /api/cart/                    # résumé du panier (JSON)
POST /api/cart/add/                # (si implémenté côté API)
POST /api/tickets/verify/          # vérifie la clé (= ticket du user connecté)
```
*Les routes redirect côté vues existent aussi :*  
`/orders/cart/add/<offer_id>/`, `/orders/cart/clear/`, `/orders/checkout/`…

---

## 5) Tests & Couverture
```powershell
python manage.py test

# Couverture rapide
coverage run manage.py test
coverage report -m
coverage html  # ouvre htmlcov/index.html
```
Périmètre fourni : modèles (Offer, Order), vue liste Offres.

---

## 6) Déploiement Fly.io (PostgreSQL)
```powershell
fly launch  # génère fly.toml

# Secrets
fly secrets set DJANGO_SECRET_KEY=... ALLOWED_HOSTS=etickets-v10.fly.dev DEBUG=0

# Base Postgres (si besoin)
fly postgres create
fly postgres attach

# Déploiement
fly deploy

# Migrations (si release_command non configurée)
fly ssh console -C "python manage.py migrate"

>>>>>>> 9ea62a1 (feat: import projet (refonte front, sécurité env, README, tests))
# Superuser
fly ssh console -C "python manage.py createsuperuser"
```


## 6. Sécurité (extraits appliqués)
- Hash MDP Django + validateurs (longueur min 10, etc.)
- CSRF activé, cookies sécurisés (selon env)
- ORM → anti-injection SQL
- Admin restreint (staff/superuser créé hors front)
- Clés : `user_key` (à l’inscription), `purchase_key` (à l’achat), `ticket_key` = hash(user_key + purchase_key)

## 7. Structure projet
accounts/  # auth & vues login/signup
offers/    # modèles & vues d'offres (+ seed_offers)
orders/    # panier, paiement mock, facture PDF
tickets/   # modèle Ticket + API verify
templates/ # templates Django (Bootstrap)
etickets/  # settings/urls/asgi/wsgi

---

## 7) Sécurité (rappels)
- Hash MDP Django + validateurs
- CSRF activé, cookies sécurisés (selon env)
- ORM Django → anti-injection SQL
- Admin restreint aux comptes staff/superuser
- **Scan** : endpoint `verify` **auth requis** + ticket lié à l’utilisateur connecté

> *Besoin d’un “poste de contrôle” qui scanne n’importe quel ticket ?*  
> Ajouter un endpoint séparé `verify_staff` (autorisé aux comptes staff) **sans filtre `user=request.user`**.

---

## 8) Structure projet
>>>>>>> 9ea62a1 (feat: import projet (refonte front, sécurité env, README, tests))
```
accounts/  # auth & vues login/signup
offers/    # modèles & vues d'offres (+ seed_offers)
orders/    # panier, paiement mock, facture PDF
<<<<<<< HEAD
tickets/   # modèle Ticket + vues scan, my_tickets
templates/ # templates Django
=======
tickets/   # modèle Ticket + API verify
templates/ # templates Django (Bootstrap)
>>>>>>> 9ea62a1 (feat: import projet (refonte front, sécurité env, README, tests))
etickets/  # settings/urls/asgi/wsgi
```

---

*Exam BLOC 3 — rendu organisé (doc, Trello, lien déployé).*
=======

## 9) Troubleshooting (FAQ)
- **PowerShell** refuse `.venv` : `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (ou utiliser `cmd` + `activate.bat`).
- **404 /static/css/theme.css** : vérifier `STATIC_URL='/static/'` et `STATICFILES_DIRS=[BASE_DIR/'static']`.  
  Prod : `STATIC_ROOT=BASE_DIR/'staticfiles'` puis `collectstatic`.
- **/my/orders/** vide ou “En attente” : l’affichage “Payée” est déterminé par la présence de tickets (`ticket_set.count > 0`).
- **Scan déconnecté** : `/api/tickets/verify/` exige un **login** → message + redirection auto vers `/login/?next=/scan/`.
- **PDF sur mobile** : ouverture en **nouvel onglet** depuis “Mes commandes”.

---

## 10) Changelog (front rapide)
- v3.1–3.5 : refonte Bootstrap, fix URLs, statics
- v3.6–3.7 : panier `/api/cart/`, montants OK
- v3.8–3.9 : “Mes tickets” (clé + QR), “Mes commandes” (lignes + total + statut)
- v3.11–3.14 : scan via API, messages login + auto‑redirect
- v3.15 : facture PDF en nouvel onglet
- v3.16–3.18 : texte home (CTA “Les offres”), titre “Bachelor Développeur d'application Python” + **badge STUDI**


---

## 11) Environnement & secrets (production)

**Principe** : aucune valeur sensible dans le code. Tout passe par **variables d’environnement**.  
Un modèle est fourni : **`.env.example`** (à copier en `.env` en local). En production, utilisez **Fly Secrets**.

### `.env.example` (standardisé)
```dotenv
DJANGO_ENV=development            # development | production
DJANGO_SECRET_KEY=change-me       # génère une clé forte en prod
DEBUG=1                           # 0 en prod
ALLOWED_HOSTS=127.0.0.1,localhost # en prod: etickets-v10.fly.dev

# CSRF (origines de confiance). En prod, mettre l’URL complète (https://...)
CSRF_TRUSTED_ORIGINS=https://etickets-v10.fly.dev

# URL d’admin personnalisable (sécurité via obscurcissement)
ADMIN_URL=admin/

# Base de données
# DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require

# Sécurité HTTPS (prod)
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=1
SECURE_HSTS_PRELOAD=1
USE_X_FORWARDED_PROTO=1

# Logs
LOG_LEVEL=INFO
```

### Secrets en production (Fly.io)
```powershell
fly secrets set DJANGO_SECRET_KEY=<clé-forte>
fly secrets set DJANGO_ENV=production
fly secrets set DEBUG=0
fly secrets set ALLOWED_HOSTS=etickets-v10.fly.dev
fly secrets set CSRF_TRUSTED_ORIGINS=https://etickets-v10.fly.dev
fly secrets set ADMIN_URL=super-admin-42/                         # optionnel mais conseillé
fly secrets set DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# Sécurité HTTPS (activée par défaut par notre settings)
fly secrets set SECURE_SSL_REDIRECT=1 SESSION_COOKIE_SECURE=1 CSRF_COOKIE_SECURE=1
fly secrets set SECURE_HSTS_SECONDS=31536000 SECURE_HSTS_INCLUDE_SUBDOMAINS=1 SECURE_HSTS_PRELOAD=1
fly secrets set USE_X_FORWARDED_PROTO=1
```

### Notes
- **Ne jamais commiter** `.env` ni aucune valeur sensible.
- `ADMIN_URL` est externe au code → changeable sans redeploy (ex. `super-admin-42/`).
- Statiques en prod via **WhiteNoise** (ajouté aux `requirements` et `MIDDLEWARE`).
- Logging vers **stdout** (`LOG_LEVEL=INFO` par défaut).
>>>>>>> 9ea62a1 (feat: import projet (refonte front, sécurité env, README, tests))
