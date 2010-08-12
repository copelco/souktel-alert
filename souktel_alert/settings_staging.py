from souktel_alert.settings import *


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "souktel_staging",
        "USER": "souktel",
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}

LOG_FILE = '/home/souktel2010/staging/rapidsms.log'
