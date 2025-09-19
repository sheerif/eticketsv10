<<<<<<< HEAD
from pathlib import Path
import os
import dj_database_url  # 👈 AJOUT

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "change-me-please")
DEBUG = os.getenv("DEBUG", "1") == "1"


ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

=======
import os
from pathlib import Path
import dj_database_url

# --- Base paths
BASE_DIR = Path(__file__).resolve().parent.parent

# === Environment (12‑factor) ===
DJANGO_ENV = os.getenv("DJANGO_ENV", "development")
def _env_bool(name, default=False):
    return os.getenv(name, "1" if default else "0").lower() in ("1","true","yes","on")

DEBUG = (os.getenv("DEBUG", "0").lower() in ("1","true","yes","on")) if DJANGO_ENV == "production" else (os.getenv("DEBUG", "1").lower() in ("1","true","yes","on"))
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key")

ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]
_origins = [o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]
CSRF_TRUSTED_ORIGINS = [o if o.startswith("http") else "https://" + o for o in _origins]

ADMIN_URL = os.getenv("ADMIN_URL", "admin/")

# --- Apps
>>>>>>> 9ea62a1 (feat: import projet (refonte front, sécurité env, README, tests))
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
<<<<<<< HEAD
=======
    # Project apps
>>>>>>> 9ea62a1 (feat: import projet (refonte front, sécurité env, README, tests))
    "accounts",
    "offers",
    "orders",
    "tickets",
<<<<<<< HEAD
    "core",
=======
>>>>>>> 9ea62a1 (feat: import projet (refonte front, sécurité env, README, tests))
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
<<<<<<< HEAD
=======
    "whitenoise.middleware.WhiteNoiseMiddleware",
>>>>>>> 9ea62a1 (feat: import projet (refonte front, sécurité env, README, tests))
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "etickets.urls"

<<<<<<< HEAD
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
=======
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
>>>>>>> 9ea62a1 (feat: import projet (refonte front, sécurité env, README, tests))

WSGI_APPLICATION = "etickets.wsgi.application"
ASGI_APPLICATION = "etickets.asgi.application"

<<<<<<< HEAD

=======
# --- Database
>>>>>>> 9ea62a1 (feat: import projet (refonte front, sécurité env, README, tests))
DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
<<<<<<< HEAD
        conn_max_age=600,   # pooling côté Django
    )
}

=======
        conn_max_age=600,
    )
}

# --- Password validation
>>>>>>> 9ea62a1 (feat: import projet (refonte front, sécurité env, README, tests))
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

<<<<<<< HEAD
=======
# --- I18N
>>>>>>> 9ea62a1 (feat: import projet (refonte front, sécurité env, README, tests))
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

<<<<<<< HEAD
#  Statics / Media (prod)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
=======
# --- Static & Media
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
>>>>>>> 9ea62a1 (feat: import projet (refonte front, sécurité env, README, tests))

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

<<<<<<< HEAD
#  Proxied HTTPS (Fly) + CSRF de confiance
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Si l’app tourne sur Fly, FLY_APP_NAME est défini → on “trust” https://<app>.fly.dev
FLY_APP_NAME = os.getenv("FLY_APP_NAME")
CSRF_TRUSTED = os.getenv("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [o for o in (CSRF_TRUSTED.split(",")) if o]  # depuis env (optionnel)
if FLY_APP_NAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{FLY_APP_NAME}.fly.dev")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

=======
# --- Auth redirects
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/my/orders/"
LOGOUT_REDIRECT_URL = "/"

# --- Security (prod)
SECURE_SSL_REDIRECT = _env_bool("SECURE_SSL_REDIRECT", True)
SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE", True)
CSRF_COOKIE_SECURE = _env_bool("CSRF_COOKIE_SECURE", True)
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000")) if DJANGO_ENV == "production" else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
SECURE_HSTS_PRELOAD = _env_bool("SECURE_HSTS_PRELOAD", True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") if _env_bool("USE_X_FORWARDED_PROTO", True) else None

# --- REST Framework
>>>>>>> 9ea62a1 (feat: import projet (refonte front, sécurité env, README, tests))
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
<<<<<<< HEAD
    "EXCEPTION_HANDLER": "core.exceptions.exception_handler",
=======
>>>>>>> 9ea62a1 (feat: import projet (refonte front, sécurité env, README, tests))
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}
<<<<<<< HEAD
=======

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
>>>>>>> 9ea62a1 (feat: import projet (refonte front, sécurité env, README, tests))
