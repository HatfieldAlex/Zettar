from pathlib import Path
import os
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent
ENV = config("ENV", default="production")
SECRET_KEY = config("SECRET_KEY")
GOOGLE_MAPS_API_KEY = config("GOOGLE_MAPS_API_KEY")
NGED_API_KEY = config("NGED_API_KEY")

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://www.zettar.tech',      
    'https://zettar-prototype-pjmq.onrender.com', 
]

if ENV == "testing":
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    DEBUG = False
    DB_NAME = config("TESTING_DB_NAME")
    DB_USER = config("TESTING_DB_USER")
    DB_PASSWORD = config("TESTING_DB_PASSWORD")
    DB_HOST = config("TESTING_DB_HOST")
    GDAL_LIBRARY_PATH = config("TESTING_GDAL_LIBRARY_PATH")
elif ENV == "local":
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    DEBUG = True
    DB_NAME = config("LOCAL_DB_NAME")
    DB_USER = config("LOCAL_DB_USER")
    DB_PASSWORD = config("LOCAL_DB_PASSWORD")
    DB_HOST = config("LOCAL_DB_HOST")
    GDAL_LIBRARY_PATH = config("LOCAL_GDAL_LIBRARY_PATH")
elif ENV == "UAT":
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    DEBUG = False
    DB_NAME = config("UAT_DB_NAME")
    DB_USER = config("UAT_DB_USER")
    DB_PASSWORD = config("UAT_DB_PASSWORD")
    DB_HOST = config("UAT_DB_HOST")
    GDAL_LIBRARY_PATH = config("UAT_GDAL_LIBRARY_PATH")
elif ENV == "production":
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    DEBUG = False
    DB_NAME = config("PROD_DB_NAME")
    DB_USER = config("PROD_DB_USER")
    DB_PASSWORD = config("PROD_DB_PASSWORD")
    DB_HOST = config("PROD_DB_HOST")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "location_input",
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

ROOT_URLCONF = "zettar_prototype.urls"

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

WSGI_APPLICATION = "zettar_prototype.wsgi.application"


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

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"