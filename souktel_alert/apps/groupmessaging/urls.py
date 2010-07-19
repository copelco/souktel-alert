#!usr/bin/env python
# encoding=utf-8

from django.conf.urls.defaults import *

from views import index
from views import messages
from views import groups
from views import recipients
from views import outgoinglog

urlpatterns = patterns('',
    url(r'^groupmessaging/?$', index.index, name='index'),
    url(r'^groupmessaging/messages/?$', messages.list, name='messages_list'),    
    url(r'^groupmessaging/messages/add/?$', messages.messageform, name='messages_add'),
    url(r'^groupmessaging/messages/send/?$', messages.send, name='messages_send'),
    url(r'^groupmessaging/messages/update/(\d+)/?$', messages.messageform, name='messages_form'),
    url(r'^groupmessaging/messages/delete/(\d+)/?$', messages.delete, name='messages_delete'),
    url(r'^groupmessaging/groups/?$', groups.list, name='groups'),
    url(r'^groupmessaging/groups/add_group/?$', groups.add, name='new_group'),
    url(r'^groupmessaging/groups/delete_group/(\d+)/?$', groups.delete, name='delete_group'),
    url(r'^groupmessaging/groups/update_group/(\d+)/?$', groups.update, name='update_group'),
    url(r'^groupmessaging/recipients/?$', recipients.list, \
        name='recipients_list'),
    url(r'^groupmessaging/recipients/(\d+)/?$', recipients.recipient, \
        name='recipient'),
    url(r'^groupmessaging/recipients/add/?$', recipients.recipient, \
        name='recipient_add'),
    url(r'^groupmessaging/recipients/add_bulk/?$', recipients.manage_recipients, \
        name='manage_recipients'),
    url(r'^groupmessaging/recipients/delete/(\d+)/?$', recipients.delete, \
        name='recipients_delete'),
    url(r'^groupmessaging/outgoinglog/?$', outgoinglog.list, \
        name='outgoinglog_list'),
    url(r'^groupmessaging/outgoinglog/filter/?$', outgoinglog.filter, \
        name='outgoinglog_filter'),
)