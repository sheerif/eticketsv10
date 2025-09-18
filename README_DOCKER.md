# Docker & Docker Compose — etickets-v10

Ce guide explique comment lancer **etickets-v10** en Docker (dev rapide) et comment utiliser `docker compose` pour gérer la base Postgres, la génération des QR (MEDIA), les migrations et les tests.

## 1) Prérequis
- Docker Desktop (Windows/Mac) ou Docker Engine (Linux)
- Docker Compose v2 (`docker compose ...`). Si tu as une ancienne version : `docker-compose ...`

## 2) Fichiers concernés
- `Dockerfile` : image Django (Python 3.13-slim + deps Pillow)
- `docker-compose.yml` : services `django` (web) + `postgres` (DB) + volume `media_data`
- `.env.example` : variables d'environnement. Copie-le en `.env` et adapte au besoin.

## 3) Variables d'environnement (.env)
Copie `.env.example` vers `.env` à la racine du projet, puis ajuste si nécessaire :
```
DJANGO_SECRET_KEY=change-me-please
DEBUG=1
ALLOWED_HOSTS=127.0.0.1,localhost
# Postgres local via docker-compose (optionnel : par défaut on tourne en SQLite):
# DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres
SERVE_MEDIA=1
```

> Par défaut (sans `DATABASE_URL`), Django utilise **SQLite** (fichier dans le projet).  
> Si tu veux **Postgres**, dé-commente `DATABASE_URL` ci-dessus.

## 4) Démarrer en mode DEV (simple, SQLite)
```bash
# à la racine du projet
docker compose up --build
```
- URL : http://localhost:8000
- QR codes générés dans le dossier **/app/media** (monté en volume : `media_data`)
- Le code hôte est bind-mounté (`.:/app`) → tes modifications sont visibles en live.

### Données de démo & admin
Dans un autre terminal :
```bash
# seed des offres (solo, duo, familiale)
docker compose exec django python manage.py seed_offers

# superuser admin (pour /admin)
docker compose exec django python manage.py createsuperuser
```

## 5) Démarrer avec **Postgres** (recommandé pour tester prod-like)
Dans `.env`, dé-commente `DATABASE_URL` (cf. 3). Puis :
```bash
docker compose up --build -d  # mode détaché
docker compose exec django python manage.py migrate
docker compose exec django python manage.py seed_offers
docker compose exec django python manage.py createsuperuser
```
- Postgres écoute sur `localhost:5432` (login: `postgres` / mdp: `postgres` ; cf. `docker-compose.yml`).

## 6) Commandes utiles
```bash
# logs en direct
docker compose logs -f django

# shell Django
docker compose exec django python manage.py shell

# exécuter un one-shot (ex: migrations)
docker compose exec django python manage.py migrate

# ouvrir un shell dans le conteneur
docker compose exec django bash

# arrêter et supprimer les conteneurs
docker compose down

# clean total (conteneurs + réseau + volume MEDIA)
docker compose down -v
```

## 7) Tests & Couverture dans Docker
```bash
docker compose exec django coverage run manage.py test
docker compose exec django coverage report -m
docker compose exec django coverage html
```
Le rapport HTML est généré dans `htmlcov/` **à l’intérieur** du conteneur. Pour l’exporter, deux options :
- Lancer les tests **sur la machine hôte** (hors conteneur) pour générer `htmlcov/` localement.
- Ou copier depuis le conteneur :  
  `docker cp $(docker compose ps -q django):/app/htmlcov ./htmlcov`

## 8) Mode “type prod” (gunicorn)
Le `docker-compose.yml` contient un exemple (commenté) pour lancer **gunicorn** au lieu du `runserver` :
```yaml
# dans docker-compose.yml (service django)
# command: gunicorn etickets.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
```
> Dans ce cas, installe `gunicorn` dans `requirements.txt` et rebuilde :  
> `docker compose up --build`

## 9) Notes & dépannage
- Si tu utilises **Windows**, évite les chemins avec espaces et exécute PowerShell en admin si besoin.
- Les QR sont générés sous `media/qr/` (volume `media_data`). Supprimer le volume **efface** ces images.
- Si une lib système manque (Pillow), rebuild : `docker compose build --no-cache`.
- Pour vérifier que Django “voit” Postgres : `docker compose exec django python -c "import dj_database_url, os; print(os.getenv('DATABASE_URL'))"`

---

**TL;DR**  
- Dev rapide : `docker compose up --build` (SQLite)  
- Prod-like : activer `DATABASE_URL` → `docker compose up -d` → `migrate + seed + createsuperuser`  
- Admin : `http://localhost:8000/admin/`
