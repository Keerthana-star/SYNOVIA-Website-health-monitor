"""
Django settings for monitor_project project.
"""

"""
Django settings for monitor_project project.
"""

from pathlib import Path
from dotenv import load_dotenv
import os
from celery.schedules import crontab

load_dotenv()  # <--- ADD THIS LINE


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
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_ENABLED = True

# --- SMS & WHATSAPP ALERTING (Twilio) ---
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')
SMS_ENABLED = True


# =================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# =================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
