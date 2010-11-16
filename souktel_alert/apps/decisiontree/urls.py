#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from django.conf.urls.defaults import *
import decisiontree.views as views

urlpatterns = patterns('',
    url(r'^tree/$', views.index, name='list-surveys'),
    url(r'^tree/(?P<id>\d+)/report/$', views.data, name='survey-report'),
    url(r'^tree/(?P<tree_id>\d+)/summary/edit/$', views.update_tree_summary,
        name='update_tree_summary'),
    url(r'^tree/(?P<tree_id>\d+)/report/sessions/$', views.recent_sessions,
        name='recent_sessions'),




    url(r'^tree/entry/list/$', views.list_entries, name='list-entries'),
    url(r'^tree/entry/(?P<entry_id>\d+)/edit/$', views.update_entry,
        name='update-entry'),
        
        
    url(r'^tree/tags/list/$', views.list_tags, name='list-tags'),
    url(r'^tree/tags/create/$', views.create_edit_tag,
        name='create-tag'),
    url(r'^tree/tags/(?P<tag_id>\d+)/edit/$', views.create_edit_tag,
        name='edit-tag'),
    url(r'^tree/tags/(?P<tag_id>\d+)/delete/$', views.delete_tag,
        name='delete-tag'),
    
    (r'^tree/data/export$', views.export),
    (r'^tree/data/export/(?P<id>\d+)$', views.export),
    url(r'^tree/data/add/$', views.addtree, name='add_tree'),
    url(r'^tree/(\d+)/$', views.addtree, name='insert_tree'),
    url(r'^tree/delete/(\d+)/$', views.deletetree, name='delete_tree'),
    url(r'^tree/survey/question/list/$', views.questionlist, name='list-questions'),
    url(r'^tree/survey/question/add/$', views.addquestion, name='add_question'),
    url(r'^tree/survey/question/update/(\d+)/$', views.addquestion, name='insert_question'),
    url(r'^tree/survey/question/delete/(\d+)/$', views.deletequestion, name='delete_question'),
    url(r'^tree/survey/answer/list/$', views.answerlist, name='answer_list'),
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
