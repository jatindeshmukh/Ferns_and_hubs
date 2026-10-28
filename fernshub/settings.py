from pathlib import Path
import os
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

# -------------------------------------------------
# Load .env if available
# -------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, using default settings
    pass

# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY",
                       "django-insecure-default-key-change-in-production")

# -------------------------------------------------
# DEBUG – this is the switch
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"

# -------------------------------------------------
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS",
                          "127.0.0.1,localhost,.onrender.com").split(",")

CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# -------------------------------------------------
# SECURITY SETTINGS – depend on DEBUG
if DEBUG:
    # ----- DEV -----
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_BROWSER_XSS_FILTER = False
    SECURE_CONTENT_TYPE_NOSNIFF = False
    SECURE_HSTS_SECONDS = 0
else:
    # ----- PROD -----
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Application Definition
# -------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'widget_tweaks',   # ✅ add this

    # Custom App
    'fronted',
]

# -------------------------------
# Middleware
# -------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -------------------------------
# URL Configuration
# -------------------------------
ROOT_URLCONF = 'fernshub.urls'

# -------------------------------
# Templates Configuration
# -------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'fronted' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'fronted.context_processors.cart_count',
                'fronted.context_processors.user_notifications',
                'fronted.context_processors.current_user',
            ],
        },
    },
]

# -------------------------------
# WSGI Application
# -------------------------------
WSGI_APPLICATION = 'fernshub.wsgi.application'

# -------------------------------
# PostgreSQL Database Configuration
# -------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    default_database = dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    if default_database['ENGINE'] != 'django.db.backends.postgresql':
        raise ValueError("This project requires PostgreSQL; DATABASE_URL must use PostgreSQL.")
else:
    default_database = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'fernshub_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
    if not default_database['PASSWORD']:
        raise ImproperlyConfigured(
            "PostgreSQL password is not configured. Set DATABASE_URL or DB_PASSWORD in .env."
        )

DATABASES = {'default': default_database}

# -------------------------------
# Password Validation
# -------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------
# Internationalization
# -------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# -------------------------------
# Static Files (CSS, JavaScript, Images)
# -------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'fronted' / 'static',
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------------------
# Media Files
# -------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -------------------------------
# Default Primary Key Field Type
# -------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------------
# Custom User Model
# -------------------------------
AUTH_USER_MODEL = 'fronted.User'

# -------------------------------
# Authentication Redirects
# -------------------------------
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# -------------------------------
# Session Settings
# -------------------------------
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True

# SESSION_COOKIE_SECURE handled above based on DEBUG

# -------------------------------
# Email Configuration
# -------------------------------
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'njogi2003@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'yrnk sfdv vdgx snsb')
DEFAULT_FROM_EMAIL = 'FernsHub <njogi2003@gmail.com>'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# -------------------------------
# Razorpay Configuration
# -------------------------------
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")

# -------------------------------
# Logging Configuration
# -------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'fronted': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# -------------------------------
# File Upload Settings
# -------------------------------
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# -------------------------------
# Cache
# -------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# -------------------------------
# Custom App Settings
# -------------------------------
FERN_SHOP_NAME = "FernsHub"
FERN_SHOP_DESCRIPTION = "Your one-stop shop for beautiful plants and gardening essentials"
FERN_SHOP_CONTACT_EMAIL = "support@fernshub.com"
FERN_SHOP_PHONE = "+91-7666804589"

FREE_SHIPPING_THRESHOLD = 500
SHIPPING_COST = 50
TAX_RATE = 5
ORDER_AUTO_CONFIRM = True
ORDER_ESTIMATED_DELIVERY_DAYS = 5