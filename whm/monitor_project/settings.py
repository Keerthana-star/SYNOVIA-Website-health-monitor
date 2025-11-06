"""
Django settings for monitor_project project.
"""

from pathlib import Path
import os
from celery.schedules import crontab

# =================================================================
# BASE CONFIGURATION
# =================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'your-secret-key'  # <-- replace with your own
DEBUG = True
ALLOWED_HOSTS = []

# =================================================================
# APPLICATION DEFINITION
# =================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django_celery_beat',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your app
    'monitor',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'monitor_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # optional
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

WSGI_APPLICATION = 'monitor_project.wsgi.application'

# =================================================================
# DATABASE CONFIGURATION
# =================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# =================================================================
# AUTHENTICATION & CUSTOM USER MODEL
# =================================================================
AUTH_USER_MODEL = 'monitor.CustomUser'

# =================================================================
# PASSWORD VALIDATION
# =================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =================================================================
# INTERNATIONALIZATION
# =================================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =================================================================
# STATIC FILES
# =================================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

# =================================================================
# LOGGING CONFIGURATION
# =================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {
        'monitor.views': {'handlers': ['console'], 'level': 'INFO', 'propagate': True},
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': True},
    },
}

# =================================================================
# CELERY CONFIGURATION
# =================================================================
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_IMPORTS = ('monitor.tasks',)

CELERY_BEAT_SCHEDULE = {
    'run-all-checks-every-minute': {
        'task': 'monitor.tasks.run_all_checks',
        'schedule': crontab(minute='*'),
    },
}

# =================================================================
# ALERTING CONFIGURATION
# =================================================================

# --- EMAIL ALERTING ---
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR.parent, 'emails.log')
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-alert-email@example.com'
EMAIL_HOST_PASSWORD = 'your-email-password'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_ENABLED = True

# --- SMS ALERTING (Twilio) ---
TWILIO_ACCOUNT_SID = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token_here'
TWILIO_PHONE_NUMBER = '+15017122661'
SMS_ENABLED = True

# =================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# =================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
