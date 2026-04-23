"""
Django settings for loja_celulares project.
Local: SQLite. Produção (Vercel, Railway, etc.): PostgreSQL via DATABASE_URL.
"""

import os
import warnings
from pathlib import Path

from dj_database_url import parse as parse_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / ".env.local")


def _env_is_true(name: str) -> bool:
    return os.environ.get(name, "").lower() in ("1", "true", "yes", "on")


def _database_url() -> str | None:
    """Railway (e outros) injetam DATABASE_URL; Vercel/Neon usam às vezes POSTGRES_URL."""
    for key in (
        "DATABASE_URL",
        "POSTGRES_URL_NON_POOLING",
        "POSTGRES_URL",
        "POSTGRES_PRISMA_URL",
        "NEON_DATABASE_URL",
    ):
        v = os.environ.get(key, "").strip()
        if v:
            return v
    return None


# Vercel: VERCEL=1, VERCEL_ENV. Railway: RAILWAY_ENVIRONMENT, RAILWAY_PROJECT_ID, etc.
_on_vercel = bool(os.environ.get("VERCEL"))
_vercel_env = os.environ.get("VERCEL_ENV", "")
_on_railway = bool(os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RAILWAY_PROJECT_ID"))
_is_cloud = _on_vercel or _on_railway

DEBUG = os.environ.get("DEBUG", "false" if _is_cloud else "true").lower() in (
    "1",
    "true",
    "yes",
)

_db_url = _database_url()
# Não bloquear o arranque (Gunicorn) se ainda não houver base: em Railway/Vercel a referência
# a DATABASE_URL em Variables pode faltar no 1.º deploy; o site usa SQLite até existir URL.
if _on_vercel and _vercel_env in ("production", "preview") and not _db_url:
    warnings.warn(
        "Vercel: sem DATABASE_URL/POSTGRES_URL. Ligue PostgreSQL (Marketplace) e as variáveis de "
        "Build com a URL. Enquanto isso, o SQLite pode ser usado (limitado no serverless).",
        UserWarning,
        stacklevel=1,
    )
if (
    _on_railway
    and (os.environ.get("RAILWAY_ENVIRONMENT", "").lower() in ("production", "staging", "preview"))
    and not _db_url
):
    warnings.warn(
        "Railway: sem DATABASE_URL. No dashboard: New > Database > PostgreSQL, depois no teu serviço "
        "web > Variables > Add Reference > seleciona o Postgres e escolhe DATABASE_URL (rede privada). "
        "Faz Redeploy. Enquanto isso, o Django usa SQLite (dados podem perder-se ao reiniciar).",
        UserWarning,
        stacklevel=1,
    )

if not DEBUG and not os.environ.get("DJANGO_SECRET_KEY"):
    raise ImproperlyConfigured(
        "Defina a variável DJANGO_SECRET_KEY (produção). Na Vercel, inclui também o ambiente de "
        "Build; na Railway, em Variables do serviço (Release/Migrate e Web usam a mesma imagem)."
    )
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-rotacione-antes-de-produção",
)

# Domínio público do Railway: *.up.railway.app; use ALLOWED_HOSTS se tiveres domínio custom.
_allowed_default = "127.0.0.1,localhost,testserver,.vercel.app,.up.railway.app"
ALLOWED_HOSTS: list[str] = [
    h.strip()
    for h in os.environ.get("ALLOWED_HOSTS", _allowed_default).split(",")
    if h.strip()
]

# Cabeçalhos de proxy: nos PaaS o edge termina SSL; use TRUST_X_FORWARDED=1 p/ Nginx local.
if _on_vercel or _on_railway or _env_is_true("TRUST_X_FORWARDED"):
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
    if _on_railway and not _csrf:
        for key in (
            "RAILWAY_SERVICE_PUBLIC_URL",
            "RAILWAY_PUBLIC_URL",
            "RAILWAY_PUBLIC_DOMAIN",
        ):
            raw = (os.environ.get(key, "") or "").strip()
            if not raw:
                continue
            if raw.startswith("https://") or raw.startswith("http://"):
                _csrf.append(raw.rstrip("/").split("?")[0])
            else:
                _csrf.append(f"https://{raw.split('/')[0]}")
            break
CSRF_TRUSTED_ORIGINS = _csrf

# HTTPS agressivo só no PaaS (Vercel/Railway) ou com USE_SSL_REDIRECT=1.
# Evita 301 com DEBUG=0 em runserver, pytest ou teste Client (sem TLS).
_in_secure_edge = _on_vercel or _on_railway
_use_https_redirect = _in_secure_edge or _env_is_true("USE_SSL_REDIRECT")

if not DEBUG:
    if _in_secure_edge or _env_is_true("USE_HTTPS_COOKIES"):
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SECURE = True
    if _use_https_redirect:
        SECURE_SSL_REDIRECT = True
        SECURE_HSTS_SECONDS = 31536000
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"

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
    "whitenoise.middleware.WhiteNoiseMiddleware",
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

if _db_url:
    DATABASES = {
        "default": parse_database_url(
            _db_url,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=_on_vercel
            or _on_railway
            or _env_is_true("POSTGRES_SSL_REQUIRE"),
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
# WhiteNoise: em produção usa compressão; em DEBUG o runserver continua a servir a pasta static/ normalmente.
if not DEBUG:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }
    WHITENOISE_MAX_AGE = 60 * 60 * 24 * 30

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
