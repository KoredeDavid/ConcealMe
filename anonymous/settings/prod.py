from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', False) == 'True'

ALLOWED_HOSTS = ['concealme.herokuapp.com', '127.0.0.1']

MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware', )

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

EMAIL_HOST = os.environ.get('EMAIL_HOST')  # The host to use for sending email.
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')  # Username to use for the SMTP server defined in EMAIL_HOST.
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')  # Password to use for the SMTP server defined in EMAIL_HOST
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_USE_TSL = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = 'mail@concealme.com'

ADMINS = [
    ('ConcealMe', SERVER_EMAIL),
]

MANAGERS = ADMINS

# Redirects 'http' to 'https'
SECURE_SSL_REDIRECT = True

import dj_database_url

prod_db = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(prod_db)
