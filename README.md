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
```powershell
# Tests Django
python manage.py test

# Couverture (rapide)
coverage run manage.py test
coverage report -m
coverage html  # ouvre htmlcov/index.html
```
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
```
accounts/  # auth & vues login/signup
offers/    # modèles & vues d'offres (+ seed_offers)
orders/    # panier, paiement mock, facture PDF
tickets/   # modèle Ticket + vues scan, my_tickets
templates/ # templates Django
etickets/  # settings/urls/asgi/wsgi
```

---
*Exam BLOC 3 — rendu organisé (doc, Trello, lien déployé).*