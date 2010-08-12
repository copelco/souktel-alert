from souktel_alert.settings import *


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "souktel_staging",
        "USER": "souktel",
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5433',
    }
}

LOG_FILE = '/home/souktel2010/staging/rapidsms.log'
