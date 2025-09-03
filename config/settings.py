from pathlib import Path
import os
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent
ENV = config("ENV", default="production")
SECRET_KEY = config("SECRET_KEY")
GOOGLE_MAPS_API_KEY = config("GOOGLE_MAPS_API_KEY")
NGED_API_KEY = config("NGED_API_KEY")
UKPN_API_KEY = config("UKPN_API_KEY")
NP_API_KEY = config("NP_API_KEY")

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

DEBUG = config(f"{ENV}_DEBUG_BOOL", cast=bool)
DB_NAME = config(f"{ENV}_DB_NAME")
DB_USER = config(f"{ENV}_DB_USER")
DB_PASSWORD = config(f"{ENV}_DB_PASSWORD")
DB_HOST = config(f"{ENV}_DB_HOST")
GDAL_LIBRARY_PATH = config(f"{ENV}_GDAL_LIBRARY_PATH", default=None)



ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://www.zettar.tech',      
    'https://zettar-prototype-pjmq.onrender.com', 
]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "pages",
    "data_pipeline",
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

ROOT_URLCONF = "config.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE"),
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": config("DB_PORT"),
    }
}


LANGUAGE_CODE = "en-gb"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"