from souktel_alert.settings import *

ADMINS = (
    ('Colin Copeland', 'copelco@caktusgroup.com'),
)
MANAGERS = ADMINS

DEFAULT_FROM_EMAIL = 'no-reply@souktel.com'
EMAIL_SUBJECT_PREFIX = '[twb-nigeria] '

EMAIL_HOST = 's2smtpout.secureserver.net'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "souktel_staging",
        "USER": "souktel2010",
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5433',
    }
}

INSTALLED_BACKENDS['javna'].update({
    'host': '208.109.191.99',
    'port': '8083',
})

LOG_FILE = '/home/souktel2010/staging/log/rapidsms.log'
