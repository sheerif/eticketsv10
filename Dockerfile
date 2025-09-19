# Base image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for psycopg, reportlab build
RUN apt-get update && apt-get install -y --no-install-recommends     build-essential     libpq-dev  && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install -r requirements.txt && pip install gunicorn

# App source
COPY . .

# Default envs (override in compose/production secrets)
ENV DJANGO_ENV=production     PORT=8000

EXPOSE 8000

# Default command (prod). In dev, docker compose overrides this.
CMD ["gunicorn", "etickets.wsgi:application", "--bind", "0.0.0.0:8000"]
