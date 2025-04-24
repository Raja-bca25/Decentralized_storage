import os
from dotenv import load_dotenv
from pathlib import Path
# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / '.env')
# Secret key (loaded from environment variable)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('DJANGO_SECRET_KEY not set in environment variables')
# Debug mode (set to False in production)
DEBUG = os.getenv('DEBUG', 'False') == 'True'
# Allowed Hosts (restrict to your domain in production)
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
# Installed Apps (no DB-related apps)
INSTALLED_APPS = [
    'django.contrib.staticfiles',  # Only need staticfiles for serving assets
    'Secure_storage',  # Your custom app
]
# Middleware (only what's needed for static files and security)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static file serving in production
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# URL Configuration (API routing)
ROOT_URLCONF = 'Secure_storage.urls'
# WSGI Application (standard WSGI setup for deployment)
WSGI_APPLICATION = 'Secure_storage.wsgi.application'
# Static files settings
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Security settings
SECURE_HSTS_SECONDS = 31536000  # One year of HTTP Strict Transport Security
SECURE_SSL_REDIRECT = True  # Redirect HTTP to HTTPS
SECURE_COOKIE_SECURE = True  # Secure cookies only on HTTPS
CSRF_COOKIE_SECURE = True  # CSRF cookie should be set only on HTTPS
SECURE_BROWSER_XSS_FILTER = True  # Enable the XSS filter
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent sniffing of content type
