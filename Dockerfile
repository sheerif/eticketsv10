# Dockerfile — simple, robust dev image for your Django project
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (Pillow, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libjpeg62-turbo-dev zlib1g-dev libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Only requirements first (better layer caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy the rest of the project (will be overridden by bind-mount in compose)
COPY . /app

# Entrypoint runs migrations, seed, etc., then execs the CMD
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Expose Django port
EXPOSE 8000

# Default command: Dev server (no extra deps like gunicorn required)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
