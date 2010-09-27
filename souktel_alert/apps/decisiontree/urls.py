#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from django.conf.urls.defaults import *
import decisiontree.views as views

urlpatterns = patterns('',
    url(r'^tree/$', views.index, name='list-surveys'),
    
    (r'^tree/data$', views.data),
    (r'^tree/data/(?P<id>\d+)/$', views.data),

    url(r'^tree/entry/list/$', views.list_entries, name='list-entries'),
    url(r'^tree/entry/(?P<entry_id>\d+)/edit/$', views.update_entry,
        name='update-entry'),

    url(r'^tree/auto-tags/list/$', views.list_auto_tags, name='list-auto-tags'),
    url(r'^tree/auto-tags/create/$', views.create_edit_auto_tag,
        name='create-auto-tag'),
    url(r'^tree/auto-tags/(?P<tag_id>\d+)/edit/$$', views.create_edit_auto_tag,
        name='edit-auto-tag'),
    
    
    (r'^tree/data/export$', views.export),
    (r'^tree/data/export/(?P<id>\d+)$', views.export),
    url(r'^tree/data/add/$', views.addtree, name='add_tree'),
    url(r'^tree/(\d+)/$', views.addtree, name='insert'),
    url(r'^tree/delete/(\d+)/$', views.deletetree, name='delete_tree'),
    url(r'^tree/survey/question/list/$', views.questionlist, name='list'),
    url(r'^tree/survey/question/add/$', views.addquestion, name='add_question'),
    url(r'^tree/survey/question/update/(\d+)/$', views.addquestion, name='insert_question'),
    url(r'^tree/survey/question/delete/(\d+)/$', views.deletequestion, name='delete_question'),
    url(r'^tree/survey/answer/list/$', views.answerlist, name='anwser_list'),
    url(r'^tree/survey/answer/add/$', views.addanswer, name='add_answer'),
    url(r'^tree/survey/answer/update/(\d+)/$', views.addanswer, name='insert_answer'),
    url(r'^tree/survey/answer/delete/(\d+)/$', views.deleteanswer, name='delete_answer'),
    url(r'^tree/survey/state/list/$', views.statelist, name='state_list'),
    url(r'^tree/survey/state/add/$', views.addstate, name='add_state'),
    url(r'^tree/survey/state/update/(\d+)/$', views.addstate, name='insert_state'),
    url(r'^tree/survey/state/delete/(\d+)/$', views.deletestate, name='delete_state'),
    url(r'^tree/survey/path/list/$', views.questionpathlist, name='path_list'),
    url(r'^tree/survey/path/add/$', views.questionpath, name='add_path'),
    url(r'^tree/survey/path/update/(\d+)/$', views.questionpath, name='insert_path'),
    url(r'^tree/survey/path/delete/(\d+)/$', views.deletepath, name='delete_path'),
    #url(r'^tree/survey/filter/$', views.filter, name='answer_filter'),
    #url(r'^tree/data/add/(\d+)/$', views.addtree, name='add'),
    # serve the static files for this TREE app
    # TODO: this should be automatic, via WEBUI
    (r'^static/tree/(?P<path>.*)$', "django.views.static.serve",
        {"document_root": os.path.dirname(__file__) + "/static"})
)
