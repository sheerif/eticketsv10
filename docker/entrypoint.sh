#!/usr/bin/env sh
set -e

echo "🔧 Running migrations..."
python manage.py migrate --noinput

# Optional: collectstatic (safe to ignore in dev)
if [ "${COLLECTSTATIC:-0}" = "1" ]; then
  echo "📦 Collecting static files..."
  python manage.py collectstatic --noinput || true
fi

# Optional: create/update superuser if env vars provided
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "👤 Ensuring superuser exists..."
  python - <<'PYCODE' || true
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "etickets.settings")
django.setup()

from django.contrib.auth import get_user_model
U = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL") or "admin@example.com"
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

u, created = U.objects.get_or_create(username=username, defaults={"email": email})
u.is_staff = True
u.is_superuser = True
u.set_password(password)
u.save()
print("Admin:", username, "(created)" if created else "(updated)")
PYCODE
fi

# Optional seed (ignore if command not present)
echo "🌱 Seeding offers (if command exists)..."
python manage.py seed_offers || true

echo "🚀 Starting app: $@"
exec "$@"
