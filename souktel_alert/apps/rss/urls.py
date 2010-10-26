from django.conf.urls.defaults import *

from rss import views


urlpatterns = patterns('',
    url(r'^rss/summary/$', views.summary, name='rss-summary'),
)
