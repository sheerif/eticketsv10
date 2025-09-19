---

## 13) Docker (dev & prod)

### A) Démarrer en **développement** (Docker Compose + Postgres)
1. Copier l’exemple d’environnement :
   ```powershell
   Copy-Item .env.docker.example .env
   ```
   > `DATABASE_URL` pointe déjà vers le service `db` du `docker-compose.yml`.

2. Lancer :
   ```powershell
   docker compose up --build
   ```

3. Initialiser la base (dans un autre terminal) :
   ```powershell
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py seed_offers
   docker compose exec web python manage.py createsuperuser
   ```

4. Accès :
   - Site : http://127.0.0.1:8000/
   - Admin : http://127.0.0.1:8000/admin/
   - Postgres : `localhost:5432` (user: `etickets_user`, pass: `change-me`, db: `etickets_db`).

> Le service `web` utilise `runserver` avec **reload** grâce au volume `.:/app`.

### B) Image **production** (Gunicorn)
Le `Dockerfile` lance par défaut :
```bash
gunicorn etickets.wsgi:application --bind 0.0.0.0:8000
```
Variables à fournir au runtime (ex. `docker run -e ...`) :
- `DJANGO_ENV=production`
- `DJANGO_SECRET_KEY=<clé-forte>`
- `ALLOWED_HOSTS=<domaine>` (ex: `etickets-v10.fly.dev`)
- `CSRF_TRUSTED_ORIGINS=https://<domaine>`
- `DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require`

Collecter les statiques si besoin :
```bash
docker run --rm --env-file .env <image> python manage.py collectstatic --noinput
```
