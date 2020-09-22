from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@6n7rh6c=vpc*kf%8+x+vg8w&pu$#bh+*@16p3q@cd*)*rf*5#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS.append('sslserver', )

BASE_DIR = os.getcwd()
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SERVER_EMAIL = 'mrconceal@gmail.com'
DEFAULT_FROM_EMAIL = SERVER_EMAIL

ADMINS = [
    ('KoredeDavid', 'koredeoluwashola@gmail.com'),
    ('Conceal', 'mrconceal@gmail.com'),
]

MANAGERS = ADMINS
