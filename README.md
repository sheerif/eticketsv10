
# eTickets JO — etickets-v10  
**Démo** : https://etickets-v10.fly.dev/  
**Trello** : https://trello.com/b/C0JIkk1g/jo-2024-studi-bloc-3-kanban

> Projet d’examen **STUDI — Bachelor Développeur d'application Python**  
> Front **Bootstrap 5** (responsive) · Panier · Tickets (QR + clé) · Scan · Facture PDF (nouvel onglet)

---

## 1) Fonctionnalités
- **Offres** (solo, duo, familiale) + ajout au **panier**
- **Compte utilisateur** (signup/login)
- **Paiement mock** → génération d’**e-tickets** (QR) basés sur 2 clés et hash **SHA-256**  
  `ticket_key = sha256(user_key + purchase_key)`
- **Mes billets** : clé + QR cliquable
- **Mes commandes** : lignes + total + **facture PDF** (`/orders/<id>/invoice.pdf`) en **nouvel onglet**
- **Scan** : `/scan/` → POST `/api/tickets/verify/` (auth requise)
- **Admin** : gestion des offres, mini report

---

## 2) Liens utiles
- **Site (démo)** : https://etickets-v10.fly.dev/
- **Trello** : https://trello.com/b/C0JIkk1g/jo-2024-studi-bloc-3-kanban
- **Admin (local)** : http://127.0.0.1:8000/admin/ (connexion avec le super utilisateur)

---

## 3) Lancer en local (Windows PowerShell)
```powershell
# 0) (si PowerShell bloque l’activation de venv)
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# 1) Environnement
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2) Base SQLite par défaut (sinon voir .env.example pour DATABASE_URL)
python manage.py migrate
python manage.py seed_offers

# 3) Créer un super utilisateur (accès /admin/)
python manage.py createsuperuser

# 4) Run
python manage.py runserver
```

**URLs utiles**
- Offres : `http://127.0.0.1:8000/offers/`  
- Login : `/login/` · Signup : `/signup/`  
- Mes commandes : `/my/orders/`  
- Mes billets : `/my/tickets/`  
- Scan : `/scan/` (connecté)  
- Admin : `/admin/` (superuser)

> Copie **`.env.example`** en **`.env`** pour surcharger `DJANGO_SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`, `CSRF_TRUSTED_ORIGINS`, `ADMIN_URL`…

---

## 4) Front (refonte)
- **Bootstrap 5** via CDN + `static/css/theme.css`
- Navbar avec **URLs nommées** Django
- **Panier** : résumé via **GET `/api/cart/`**
- **Facture PDF** : lien `target="_blank"` (mobile-friendly)
- **/scan/** : form **POST** `/api/tickets/verify/` (CSRF inclus)  
  → Déconnecté : message + redirection auto vers `/login/?next=/scan/`

---

## 5) API (extraits)
```
GET  /api/cart/                    # résumé du panier (JSON)
POST /api/tickets/verify/          # vérifie la clé (user connecté)
```
*Routes redirect vues :* `/orders/cart/add/<offer_id>/`, `/orders/cart/clear/`, `/orders/checkout/`…

---

## 6) Tests & Couverture
```powershell
# Tests Django
python manage.py test

# Couverture (rapide)
coverage run manage.py test
coverage report -m
coverage html  # ouvre htmlcov/index.html
```

---

## 7) Déploiement Fly.io (PostgreSQL)
```powershell
fly launch  # si premier setup

# Secrets (⚠️ jamais commiter)
fly secrets set DJANGO_SECRET_KEY=<clé-forte>
fly secrets set DJANGO_ENV=production DEBUG=0
fly secrets set ALLOWED_HOSTS=etickets-v10.fly.dev
fly secrets set CSRF_TRUSTED_ORIGINS=https://etickets-v10.fly.dev
fly secrets set ADMIN_URL=super-admin-42/
fly secrets set DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# Déploiement
fly deploy
# Migrations (si nécessaire)
fly ssh console -C "python manage.py migrate"
# Superuser (si besoin)
fly ssh console -C "python manage.py createsuperuser"
```

---

## 8) Sécurité (appliquée)
- **12-factor** via variables d’environnement (`dj-database-url`)
- **HTTPS/HSTS** + cookies sécurisés  
  (`SECURE_SSL_REDIRECT`, `SECURE_HSTS_*`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`)
- **Admin** externalisé via `ADMIN_URL`
- **WhiteNoise** pour les statiques (prod)
- ORM Django, CSRF, validateurs de mots de passe

---

## 9) Structure projet
```
accounts/  # auth & vues login/signup
offers/    # modèles & vues d'offres (+ seed_offers)
orders/    # panier, paiement mock, facture PDF
tickets/   # modèle Ticket + API verify
templates/ # templates Django (Bootstrap)
etickets/  # settings/urls/asgi/wsgi
```

---

## 10) Troubleshooting (FAQ)
- **Venv bloquée** : `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (ou `cmd` + `activate.bat`)
- **Statique 404** : `STATIC_URL='/static/'`, `STATICFILES_DIRS=[BASE_DIR/'static']`; prod : `STATIC_ROOT` + `collectstatic`
- **/my/orders/** “En attente” : statut basé sur présence de tickets (`ticket_set.count > 0`)
- **Scan déconnecté** : `verify` nécessite login (normal)
- **PDF mobile** : lien en **nouvel onglet**

---

## 11) Environnement & secrets (production)
Modèle fourni : **`.env.example`** (copier en `.env` en local).  
En prod, **injecter via Fly Secrets** — jamais dans le repo.

```dotenv
DJANGO_ENV=development
DJANGO_SECRET_KEY=change-me
DEBUG=1
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=https://etickets-v10.fly.dev
ADMIN_URL=admin/
# DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=1
SECURE_HSTS_PRELOAD=1
USE_X_FORWARDED_PROTO=1
LOG_LEVEL=INFO
```

---

## 12) Changelog (front rapide)
- v3.1–3.5 : refonte Bootstrap, fix URLs, statics  
- v3.6–3.7 : panier `/api/cart/`  
- v3.8–3.9 : “Mes tickets” (clé + QR), “Mes commandes” (statut + total)  
- v3.11–3.14 : scan via API, login redirect  
- v3.15 : facture PDF en nouvel onglet  
- v3.16–3.18 : Home “Les offres”, titre **Bachelor Développeur d'application Python** + badge **STUDI**
