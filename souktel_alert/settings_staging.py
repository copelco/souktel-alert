from souktel_alert.settings import *


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
