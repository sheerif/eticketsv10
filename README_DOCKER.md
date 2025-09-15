# Docker (dev) for your Django project

## Files
- `Dockerfile` — Python 3.13 slim, installs `requirements.txt`, exposes port 8000.
- `docker/entrypoint.sh` — runs `migrate`, optional `collectstatic`, ensures admin (if env set), seeds offers, then starts the server.
- `docker-compose.yml` — binds port 8000, mounts your source into the container, loads env from `.env`.
- `.env` — sample is included as `.env` (you can keep or change values).

## Quickstart
```bash
# from the project root (same folder as manage.py & requirements.txt)
docker compose up --build
# open http://localhost:8000
```

### Optional: admin auto-creation
Set these in `.env` before `docker compose up`:
```
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=Passw0rd!234
```

### Notes
- By default the container runs `python manage.py runserver 0.0.0.0:8000`.
- Your code is bind-mounted (`./:/app`), so edits on the host are reflected inside.
- SQLite DB file stays in your project folder (persisted on host).
- If you install `gunicorn` in `requirements.txt`, you can switch the command in `docker-compose.yml` as shown in the comment.
