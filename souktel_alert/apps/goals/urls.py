from django.conf.urls.defaults import *

from goals import views


urlpatterns = patterns('',
    url(r'^goals/summary/$', views.summary, name='goals-summary'),
)
