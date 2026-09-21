from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass


# =========================
# Django asosiy sozlamalari
# =========================

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-local-only"
)

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    ".railway.app",
    "taklifnoma-project-wvlur.faable.link",
]


# =========================
# Ilovalar
# =========================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "bosh_sahifa",
    "bosh_sahifa2",
    "toylar",
]


# =========================
# Middleware
# =========================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================
# URL va Template
# =========================

ROOT_URLCONF = "bosh_sahifa.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates"
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =========================
# WSGI
# =========================

WSGI_APPLICATION = "bosh_sahifa.wsgi.application"


# =========================
# Database
# =========================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# =========================
# Password validation
# =========================

AUTH_PASSWORD_VALIDATORS = []


# =========================
# Til va vaqt
# =========================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Tashkent"

USE_I18N = True

USE_TZ = True


# =========================
# Static files
# =========================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

STATICFILES_DIRS = [
    BASE_DIR / "static"
]


# =========================
# Default primary key
# =========================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =========================
# Telegram bot
# =========================

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    ""
).strip()

TELEGRAM_ADMIN_ID = os.getenv(
    "TELEGRAM_ADMIN_ID",
    ""
).strip()

TELEGRAM_ADMIN_USERNAME = os.getenv(
    "TELEGRAM_ADMIN_USERNAME",
    ""
).strip()

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    TELEGRAM_ADMIN_ID
).strip()


# =========================
# Sayt manzili
# =========================

SITE_URL = os.getenv(
    "SITE_URL",
    "https://taklifnoma-fatxulla-zeboxon.vercel.app/"
).strip()


# =========================
# CSRF
# =========================

CSRF_TRUSTED_ORIGINS = [
    "https://taklifnoma-project-wvlur.faable.link",
]


# =========================
# Production xavfsizlik
# =========================

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https"
    )

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True