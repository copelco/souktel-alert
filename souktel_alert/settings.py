#!/usr/bin/env python
# vim: et ts=4 sw=4


# inherit everything from rapidsms, as default
# (this is optional. you can provide your own.)
from rapidsms.djangoproject.settings import *


# then add your django settings:

DEBUG = True

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
    "rapidsms.contrib.scheduler",

    # enable the django admin using a little shim app (which includes
    # the required urlpatterns)
    # This is just a comment
    "rapidsms.contrib.djangoadmin",
    "django.contrib.admin",
    'djangotables',
    'groupmessaging',
    'rclickatell',
    'xforms',
    'uni_form',
    "rclickatell",
    "rerouter",
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TABS = [
    ('rapidsms.views.dashboard', 'Dashboard'),
    ('rapidsms.contrib.httptester.views.generate_identity', 'Message Tester'),
    ('rapidsms.contrib.messagelog.views.message_log', 'Message Log'),
    ('rapidsms.contrib.messaging.views.messaging', 'Messaging'),
    ('groupmessaging.views.index.index', 'Group Messaging'),
    ('xforms.views.xforms', 'XForms'),
    ('rclickatell.views.test', 'Clickatell'),
]

INSTALLED_BACKENDS = {
    "clickatell": {"ENGINE": "rclickatell.backend"},
    "javna": {"ENGINE": "rjavna.backend"},
    "message_tester" : {"ENGINE": "rapidsms.backends.bucket"},
}

XFORMS_HOST="192.168.10.20:8000"
TEST_RUNNER = "django_nose.run_tests"

REROUTE = {
    'javna': 'clickatell',
}
