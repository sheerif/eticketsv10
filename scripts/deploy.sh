#!/bin/bash
# Enhanced deployment script for production

set -e

echo "🚀 Starting production deployment..."

# Check if required environment variables are set
required_vars=("DJANGO_SECRET_KEY" "DATABASE_URL" "ALLOWED_HOSTS")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var environment variable is not set"
        exit 1
    fi
done

# Set production environment
export DJANGO_ENV=production
export DEBUG=0

echo "🔧 Installing dependencies..."
pip install -r requirements.txt --no-cache-dir

echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "🧪 Running health checks..."
python manage.py check --deploy

echo "🌱 Seeding initial data (if needed)..."
python manage.py seed_offers || echo "Offers already seeded"

echo "👤 Creating superuser (if needed)..."
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py shell << EOF
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ['DJANGO_SUPERUSER_USERNAME']
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ['DJANGO_SUPERUSER_PASSWORD']
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superuser {username} created')
else:
    print(f'Superuser {username} already exists')
EOF
fi

echo "🔍 Validating deployment..."
python -c "
import django
django.setup()
from django.core.management import call_command
call_command('check', verbosity=0)
print('✅ All checks passed')
"

echo "🎉 Deployment completed successfully!"

# Start the application
if [ "$1" = "--start" ]; then
    echo "🚀 Starting Gunicorn server..."
    exec gunicorn etickets.wsgi:application \
        --bind 0.0.0.0:${PORT:-8000} \
        --workers ${WEB_CONCURRENCY:-4} \
        --worker-class gevent \
        --worker-connections 1000 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --timeout 30 \
        --keep-alive 2 \
        --log-level info \
        --access-logfile - \
        --error-logfile -
fi