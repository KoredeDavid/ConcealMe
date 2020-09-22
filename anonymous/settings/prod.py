from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret_setting('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["conceal.azurewebsites.net",]

MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware',)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DBNAME', ''),
        'USER': os.environ.get('DBUSER', ''),
        'PASSWORD': os.environ.get('DBPASS', ''),
        'HOST': os.environ.get('DBHOST', ''),
        'PORT': os.environ.get('DBPORT', ''),

    }
}
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

EMAIL_HOST_USER = get_secret_setting('EMAIL_HOST_USER')
EMAIL_HOST = get_secret_setting('EMAIL_HOST')
EMAIL_HOST_PASSWORD = get_secret_setting('EMAIL_HOST_PASSWORD')
EMAIL_PORT = get_secret_setting('EMAIL_PORT')
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

SERVER_EMAIL = 'mrconceal@gmail.com'
DEFAULT_FROM_EMAIL = SERVER_EMAIL

ADMINS = [
    ('KoredeDavid', 'koredeoluwashola@gmail.com'),
    ('Conceal', 'mrconceal@gmail.com'),
]

MANAGERS = ADMINS

