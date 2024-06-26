"""
Django settings for earninja project.

Generated by 'django-admin startproject' using Django 4.2.11.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-tt=_^2aiirpsiwx4!xb@gvoi0jcu-@_&!r7pc8zi)8ty76n7aw')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['tgrykias.eu.pythonanywhere.com', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ['https://tgrykias.eu.pythonanywhere.com']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'exercises.apps.ExercisesConfig',
    'accounts',
    'django_extensions',
    'django_cleanup.apps.CleanupConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'earninja.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'earninja.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# Update database configuration from $DATABASE_URL environment variable (if defined)
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=500,
        conn_health_checks=True,
    )


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Media files (.mp3)
# https://docs.djangoproject.com/en/4.2/topics/files/

MEDIA_ROOT = BASE_DIR / 'media/'
MEDIA_URL = 'media/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / "static"]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# security settings for deployment

# https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/#https
# https://docs.djangoproject.com/en/4.2/topics/security/#ssl-https
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False') == 'True'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'

# https://docs.djangoproject.com/en/4.2/ref/middleware/#http-strict-transport-security
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', 0))
SECURE_HSTS_PRELOAD = os.environ.get('SECURE_HSTS_PRELOAD', 'False') == 'True'
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False') == 'True'

# crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# https://docs.djangoproject.com/en/4.2/ref/settings/#login-redirect-url
# https://docs.djangoproject.com/en/4.2/ref/settings/#logout-redirect-url
LOGIN_REDIRECT_URL = "exercises:choose_exercise"
LOGOUT_REDIRECT_URL = "exercises:choose_exercise"

# AudioSaver
# parameters for generation of audio files for exercises

# required for conversion of midi to wav with fluidsynth
# https://github.com/FluidSynth/fluidsynth/wiki/SoundFont
SOUNDFONT_PATH = os.getenv('SOUNDFONT_PATH')
FLUIDSYNTH_PATH = os.getenv('FLUIDSYNTH_PATH')

# by default fluidsynth output is quiet
# this setting is for how much to increase volume of the sound in exercises
# volume is increased using pydub
# https://github.com/jiaaro/pydub
NUM_DB_LOUDER = 20

# it's possible to make sound louder by increasing
# gain passed to fluidsynth
# it can distort sound though
FLUIDSYNTH_GAIN = 0.2
FLUIDSYNTH_SAMPLE_RATE = 44100

# Celery settings
# Celery it not supported on PythonAnywhere
# so in production, audio file generation runs synchronously
USE_CELERY = False

CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"

# default setttings for intervals exercise
INTERVALS_EXERCISE_DEFAULT_LOWEST_OCTAVE = 2
INTERVALS_EXERCISE_DEFAULT_HIGHEST_OCTAVE = 5
INTERVALS_EXERCISE_DEFAULT_ALLOWED_INTERVALS = ["1", "b3", "3", "4", "5"]
# 0 - harmonic, 1 - melodic ascending, 2 - melodic descending
INTERVALS_EXERCISE_DEFAULT_INTERVAL_TYPE = 0
