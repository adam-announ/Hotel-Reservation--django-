import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-votre-clé-secrète-change-moi-en-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Applications tierces
    'crispy_forms',
    'crispy_bootstrap4',  # Si vous utilisez bootstrap 4
    
    # Applications du projet
    'accounts',
    'rooms',
    'reservations',
    'reports',
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

ROOT_URLCONF = 'hotel_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'hotel_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
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
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Pour la production

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Authentication
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

# ==================== EMAIL CONFIGURATION ====================

# IMPORTANT: Pour envoyer de vrais emails (remplacez les valeurs par les vôtres)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Configuration Gmail/Google Workspace
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# Variables d'email (sécurisées avec des variables d'environnement)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'yassmine@hoteldeluxe.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

# Email par défaut pour l'expéditeur
DEFAULT_FROM_EMAIL = f'Hôtel Deluxe <{EMAIL_HOST_USER}>'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Configuration pour les erreurs serveur
ADMINS = [
    ('Admin Hotel', EMAIL_HOST_USER),
]

# Timeout pour les connexions email
EMAIL_TIMEOUT = 30

# ==================== CONFIGURATION ALTERNATIVE ====================

# Si vous préférez configurer directement (TEMPORAIRE pour les tests)
# Remplacez ces valeurs par vos propres identifiants Gmail :

# EMAIL_HOST_USER = 'votre-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'votre-mot-de-passe-app-gmail'  # Mot de passe d'application !

# ==================== AUTRES FOURNISSEURS EMAIL ====================

# Pour Outlook/Hotmail (décommentez et configurez si nécessaire)
# EMAIL_HOST = 'smtp-mail.outlook.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True

# Pour Yahoo Mail (décommentez et configurez si nécessaire)
# EMAIL_HOST = 'smtp.mail.yahoo.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True

# Pour un serveur SMTP personnalisé (décommentez et configurez si nécessaire)
# EMAIL_HOST = 'mail.votre-domaine.com'
# EMAIL_PORT = 587  # ou 465 pour SSL
# EMAIL_USE_TLS = True  # ou EMAIL_USE_SSL = True

# ==================== FIN CONFIGURATION EMAIL ====================

# Session settings
SESSION_COOKIE_AGE = 3600 * 24 * 14  # 14 jours en secondes
SESSION_SAVE_EVERY_REQUEST = True

# Security settings (à activer en production)
if not DEBUG:
    SECURE_HSTS_SECONDS = 3600  # 1 heure
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# ==================== LOGGING CONFIGURATION ====================

# Configuration du logging pour les emails
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'hotel_email.log'),
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'hotel_email': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Créer le dossier de logs s'il n'existe pas
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)