"""
Django settings for huella_urbana project.
"""

from pathlib import Path
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------
# 🔐 SECRET KEY
# ------------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "local-secret-key-123")

DEBUG = True
ALLOWED_HOSTS = ["*"]

# ------------------------------------
# ☁️ CLOUDINARY CONFIG - DEBE IR ANTES DE INSTALLED_APPS
# ------------------------------------
cloudinary.config( 
  cloud_name = "dkvukgf3z",
  api_key = "934128825581411",
  api_secret = "C0Pt-M78d9UU2rWePMFyxGlbRhs",
  secure = True
)
# ⚠️ IMPORTANTE: Esta línea hace que Django use Cloudinary automáticamente
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# NO necesitas MEDIA_ROOT ni MEDIA_URL con Cloudinary
MEDIA_URL = "/media/"

# ------------------------------------
# 🔐 LOGIN SYSTEM
# ------------------------------------
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ------------------------------------
# 📦 INSTALLED APPS
# ------------------------------------
INSTALLED_APPS = [
    'jazzmin',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    # CLOUDINARY - IMPORTANTE: en este orden
    'cloudinary',
    'cloudinary_storage',

    'django.contrib.staticfiles',

    'server.apps.ServerConfig',
    'widget_tweaks',
    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
]

SITE_ID = 1

# ------------------------------------
# 📧 EMAIL CONFIG
# ------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "katalinagatita7520@gmail.com"
EMAIL_HOST_PASSWORD = "laan joxu incf yzjz"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ------------------------------------
# 🛡️ MIDDLEWARE
# ------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ------------------------------------
# ⚙️ URLS / WSGI
# ------------------------------------
ROOT_URLCONF = 'huella_urbana.urls'
WSGI_APPLICATION = 'huella_urbana.wsgi.application'

# ------------------------------------
# 🖼️ TEMPLATES
# ------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ------------------------------------
# 🗄️ DATABASE
# ------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ------------------------------------
# 🔐 PASSWORD RULES
# ------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------------
# 🌎 TIMEZONE
# ------------------------------------
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# ------------------------------------
# 🗂️ STATIC FILES
# ------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ------------------------------------
# ⚡ AUTO FIELD
# ------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'