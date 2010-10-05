#!usr/bin/env python
# encoding=utf-8

from django.conf.urls.defaults import *

from views import index
from views import messages
from views import groups
from views import recipients
from views import outgoinglog
from views import incominglog


urlpatterns = patterns('',
    url(r'^$', index.index, name='index'),
    url(r'^group-messaging/messages/$', messages.list, name='messages_list'),
    url(r'^group-messaging/incominglog/$', incominglog.message_log, name='incoming_log'),
    url(r'^group-messaging/messages/add/$', messages.messageform, name='messages_add'),
    url(r'^group-messaging/messages/send/$', messages.send, name='messages_send'),
    url(r'^group-messaging/messages/update/(\d+)/$', messages.messageform, name='messages_form'),
    url(r'^group-messaging/messages/delete/(\d+)/$', messages.delete, name='messages_delete'),
    url(r'^group-messaging/groups/$', groups.list, name='groups'),
    url(r'^group-messaging/groups/add_group/$', groups.add, name='new_group'),
    url(r'^group-messaging/groups/delete_group/(\d+)/$', groups.delete, name='delete_group'),
    url(r'^group-messaging/groups/update_group/(\d+)/$', groups.update, name='update_group'),
    url(r'^group-messaging/recipients/$', recipients.list_recipients, \
        name='list_recipients'),
    url(r'^group-messaging/recipients/(\d+)/$', recipients.recipient, \
        name='update_recipient'),
    url(r'^group-messaging/recipients/add/$', recipients.recipient, \
        name='recipient_add'),
    url(r'^group-messaging/recipients/add_bulk/$', recipients.manage_recipients, \
        name='manage_recipients'),
    url(r'^group-messaging/recipients/delete/(\d+)/$', recipients.delete, \
        name='recipients_delete'),
    url(r'^group-messaging/outgoinglog/$', outgoinglog.list, \
        name='outgoinglog_list'),
    #url(r'^group-messaging/outgoinglog/filter/$', outgoinglog.filter, \
    #    name='outgoinglog_filter'),
)