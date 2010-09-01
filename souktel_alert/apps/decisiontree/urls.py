#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from django.conf.urls.defaults import *
import decisiontree.views as views

urlpatterns = patterns('',
    (r'^tree$', views.index),
    
    (r'^tree/data$', views.data),
    (r'^tree/data/(?P<id>\d+)$', views.data),
    
    (r'^tree/data/export$', views.export),
    (r'^tree/data/export/(?P<id>\d+)$', views.export),
    url(r'^tree/data/add/?$', views.addtree, name='add_tree'),
    url(r'^tree/(\d+)/?$', views.addtree, name='insert'),
    url(r'^tree/delete/(\d+)/?$', views.deletetree, name='delete_tree'),
    url(r'^tree/survey/question/list/?$', views.questionlist, name='list'),
    url(r'^tree/survey/question/add/?$', views.addquestion, name='add_question'),
    url(r'^tree/survey/question/update/(\d+)/?$', views.addquestion, name='insert_question'),
    url(r'^tree/survey/question/delete/(\d+)/?$', views.deletequestion, name='delete_question'),
    #url(r'^tree/data/add/(\d+)/?$', views.addtree, name='add'),
    # serve the static files for this TREE app
    # TODO: this should be automatic, via WEBUI
    (r'^static/tree/(?P<path>.*)$', "django.views.static.serve",
        {"document_root": os.path.dirname(__file__) + "/static"})
)
