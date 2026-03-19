import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── SÉCURITÉ ─────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-remplacez-cette-cle-en-production')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# ─── APPLICATIONS ─────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts.apps.AccountsConfig',
    'dashboard.apps.DashboardConfig',
    'builder.apps.BuilderConfig',
    'billing.apps.BillingConfig',
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
    'builder.middleware.SiteRouterMiddleware',
]

ROOT_URLCONF = 'siteforge.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'siteforge.wsgi.application'

# ─── BASE DE DONNÉES ──────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ─── AUTH ─────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
]

# ─── STATIQUES ────────────────────────────────────────────────────────────────
STATIC_URL = '/static/'

# N'ajouter le dossier static/ que s'il existe (évite le warning sur Render)
_STATIC_DIR = BASE_DIR / 'static'
if _STATIC_DIR.exists():
    STATICFILES_DIRS = [_STATIC_DIR]
else:
    STATICFILES_DIRS = []

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── STRIPE ───────────────────────────────────────────────────────────────────
STRIPE_PUBLIC_KEY     = os.environ.get('STRIPE_PUBLIC_KEY', 'pk_test_xxx')
STRIPE_SECRET_KEY     = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_xxx')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_xxx')
MONTHLY_PRICE_ID      = os.environ.get('MONTHLY_PRICE_ID', 'price_xxx')
YEARLY_PRICE_ID       = os.environ.get('YEARLY_PRICE_ID', 'price_xxx')

# ─── DIVERS ───────────────────────────────────────────────────────────────────
TRIAL_DAYS        = int(os.environ.get('TRIAL_DAYS', 21))
EMAIL_BACKEND     = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@siteforge.io'
MAIN_DOMAIN       = os.environ.get('MAIN_DOMAIN', 'localhost:8000')

SESSION_ENGINE    = 'django.contrib.sessions.backends.db'
MESSAGE_STORAGE   = 'django.contrib.messages.storage.session.SessionStorage'
X_FRAME_OPTIONS   = 'SAMEORIGIN'
