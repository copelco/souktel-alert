#!usr/bin/env python
# encoding=utf-8

from django.conf.urls.defaults import *
from rclickatell import views


urlpatterns = patterns('',
    url(r'^clickatell/?$', views.test, name='clickatell'),
)
