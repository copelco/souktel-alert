#!/usr/bin/env python
# encoding=utf-8
import logging

from django import forms
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext
from django.forms.formsets import formset_factory

from group_messaging.models import OutgoingLog
from group_messaging.decorators import contact_required
from rapidsms.contrib.messagelog import *

from django.template import RequestContext
from django.shortcuts import render_to_response
from rapidsms.contrib.messagelog.tables import MessageTable
from rapidsms.contrib.messagelog.models import Message
from group_messaging.forms import messageslogFilter





@contact_required
def message_log(req):

    count = Message.objects.count()
    messages_log = Message.objects.all()
    messagelogfilter = messageslogFilter(req.GET, queryset=Message.objects.all())
    mycontext = {"messagelogfilter": messagelogfilter,"messages_log": messages_log,"count": count,"messages_table": MessageTable(Message.objects.all(), request=req)}
    context = (mycontext)
    return render_to_response("incoming.html",context, context_instance=RequestContext(req))

