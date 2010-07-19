#!/usr/bin/env python
# vim: et ts=4 sw=4


# inherit everything from rapidsms, as default
# (this is optional. you can provide your own.)
from rapidsms.djangoproject.settings import *


# then add your django settings:

DEBUG = True

DATABASE_ENGINE = "sqlite3"
DATABASE_NAME = "db.sqlite3"

INSTALLED_APPS = [
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    'django.contrib.humanize',
    "rapidsms",
    "rapidsms.contrib.ajax", 
    "rapidsms.contrib.httptester", 
    "rapidsms.contrib.handlers", 
    "rapidsms.contrib.echo",
    "rapidsms.contrib.messagelog",
    "rapidsms.contrib.messaging",

    # enable the django admin using a little shim app (which includes
    # the required urlpatterns)
    "rapidsms.contrib.djangoadmin",
    "django.contrib.admin",
    'djangotables',
    'groupmessaging',
]

TABS = [
    ('rapidsms.views.dashboard', 'Dashboard'),
    ('rapidsms.contrib.httptester.views.generate_identity', 'Message Tester'),
    ('rapidsms.contrib.messagelog.views.message_log', 'Message Log'),
    ('rapidsms.contrib.messaging.views.messaging', 'Messaging'),
    ('groupmessaging.views.index.index', 'Group Messaging'),
]
