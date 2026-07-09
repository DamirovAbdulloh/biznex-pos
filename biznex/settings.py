import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Desktop (PyInstaller) rejimida ma'lumotlar papkasi foydalanuvchi kompyuterida,
# .exe fayl yonida saqlanadi (yozish huquqi bo'lishi uchun)
DESKTOP_MODE = os.environ.get('BIZNEX_DESKTOP') == '1'
DATA_DIR = Path(os.environ.get('BIZNEX_DATA_DIR', BASE_DIR)) if DESKTOP_MODE else BASE_DIR

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-biznex-secret-key-2026')

# Railway/production'da DEBUG=False bo'lishi kerak (env orqali boshqariladi)
DEBUG = os.environ.get('DEBUG', 'True' if DESKTOP_MODE else 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Railway avtomatik beradigan domen (masalan: biznex.up.railway.app)
RAILWAY_PUBLIC_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
if RAILWAY_PUBLIC_DOMAIN and RAILWAY_PUBLIC_DOMAIN not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)

CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS if h and h != '*']

# Railway https orqali proxy qiladi — xavfsizlik sozlamalari faqat production'da (DEBUG=False)
if not DEBUG and not DESKTOP_MODE:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'orders',
    'products',
    'employees',
    'reports',
    'locations',
    'transactions',
    'clients',
    'smena',
    'warehouse',
    'settings_app',
    'syncing',
]

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'biznex.middleware.AdminAuthMiddleware',
]

ROOT_URLCONF = 'biznex.urls'
WSGI_APPLICATION = 'biznex.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': DEBUG,  # production'da qo'lda cached loader ishlatiladi (pastda)
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
if not DEBUG:
    # Shablonlarni har so'rovda qayta o'qib-tahlil qilish o'rniga xotirada keshlaydi —
    # sahifalar sezilarli tezroq ochiladi
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and not DESKTOP_MODE:
    # Faqat saytda (Railway) ishlatiladi. Desktop endi umumiy bazaga to'g'ridan-to'g'ri
    # ulanmaydi — buning o'rniga syncing ilovasi orqali fon rejimida sinxronlashadi
    # (internet yo'qligida ham desktop to'liq mustaqil, xatosiz ishlashi uchun).
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    # Desktop — har doim mahalliy SQLite (internet bo'lmasa ham to'liq ishlaydi)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': DATA_DIR / 'db.sqlite3',
        }
    }

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = DATA_DIR / 'staticfiles'
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# DEBUG rejimida ham whitenoise orqali static fayllarni to'g'ridan-to'g'ri
# STATICFILES_DIRS'dan berish (desktop ilovada collectstatic shart emas)
WHITENOISE_USE_FINDERS = DEBUG
WHITENOISE_AUTOREFRESH = DEBUG

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Sinxronizatsiya (desktop <-> sayt) ---
# SYNC_API_KEY: ikkala tomonda (saytda va desktop config.json'da) BIR XIL bo'lishi shart —
# bu API kalitisiz hech kim /sync/pull/ yoki /sync/push/ ga murojaat qila olmaydi.
SYNC_API_KEY = os.environ.get('SYNC_API_KEY', '')
# SYNC_REMOTE_URL: faqat desktop ilova tomonida ishlatiladi (config.json orqali
# muhitga o'rnatiladi) — desktop shu manzilga pull/push qiladi. Saytning o'zida bo'sh qoladi.
SYNC_REMOTE_URL = os.environ.get('SYNC_REMOTE_URL', '')

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# Sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
