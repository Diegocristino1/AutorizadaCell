"""
Django settings for loja_celulares project.
Local: SQLite. Produção (Vercel): PostgreSQL via DATABASE_URL.
"""

import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / ".env.local")


def _env_is_true(name: str) -> bool:
    return os.environ.get(name, "").lower() in ("1", "true", "yes", "on")


# Vercel define VERCEL=1. VERCEL_ENV: development (vercel dev), preview, production.
_on_vercel = bool(os.environ.get("VERCEL"))
_vercel_env = os.environ.get("VERCEL_ENV", "")
DEBUG = os.environ.get("DEBUG", "false" if _on_vercel else "true").lower() in (
    "1",
    "true",
    "yes",
)

if (
    _on_vercel
    and _vercel_env in ("production", "preview")
    and not os.environ.get("DATABASE_URL")
):
    raise ImproperlyConfigured(
        "Na Vercel (preview/produção), defina DATABASE_URL com um PostgreSQL. "
        "Crie o banco no painel (Storage) ou use Neon/Supabase e ligue as variáveis."
    )

if not DEBUG and not os.environ.get("DJANGO_SECRET_KEY"):
    raise ImproperlyConfigured(
        "Defina a variável de ambiente DJANGO_SECRET_KEY no projeto (ex.: chave longa e aleatória)."
    )
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-rotacione-antes-de-produção",
)

_allowed_default = "127.0.0.1,localhost,testserver,.vercel.app"
ALLOWED_HOSTS: list[str] = [
    h.strip()
    for h in os.environ.get("ALLOWED_HOSTS", _allowed_default).split(",")
    if h.strip()
]

if _on_vercel or not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True

_csrf: list[str] = []
if raw := os.environ.get("CSRF_TRUSTED_ORIGINS"):
    _csrf = [o.strip() for o in raw.split(",") if o.strip()]
else:
    vercel_url = os.environ.get("VERCEL_URL", "")
    if vercel_url:
        host = vercel_url.replace("https://", "").replace("http://", "").split("/")[0]
        if host:
            _csrf.append(f"https://{host}")
CSRF_TRUSTED_ORIGINS = _csrf

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "catalog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "loja_celulares.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "catalog.context_processors.social_links",
            ],
        },
    },
]

WSGI_APPLICATION = "loja_celulares.wsgi.application"

if os.environ.get("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=_on_vercel or _env_is_true("POSTGRES_SSL_REQUIRE"),
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

USE_THOUSAND_SEPARATOR = True
DECIMAL_SEPARATOR = ","
THOUSAND_SEPARATOR = "."

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Somente dígitos com DDI (ex.: 5511999998888). Ajuste para o número real da loja.
WHATSAPP_PHONE = "5561996446665"
WHATSAPP_DEFAULT_MESSAGE = (
    "Olá! Vim pelo site da Autorizada Cell e quero falar sobre os celulares."
)

# URL completa do perfil no Instagram.
INSTAGRAM_URL = "https://www.instagram.com/autorizadacell/"

# Localização da loja (Brasília/DF — SIA).
STORE_LOCALE = "Brasília/DF — Setor SIA (Setor de Indústrias e Abastecimento)"
STORE_ASSISTANCE_ADDRESS = (
    "Loja de assistência técnica: SIA, Bloco D, salas 229 e 230 — Brasília/DF"
)
