#!/usr/bin/env python
# encoding=utf-8
import logging
import csv

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
def message_log(request):
    messages = Message.objects.select_related('contact',
                                              'connection__backend')
    messages = messages.order_by('-date')
    paginator = Paginator(messages, 25)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        messagelog = paginator.page(page)
    except (EmptyPage, InvalidPage):
        messagelog = paginator.page(paginator.num_pages)

    messagelogfilter = messageslogFilter(request.GET, queryset=messages)
    context = {
        "messagelogfilter": messagelogfilter,
        "messages_log": messages,
        "messagelog":messagelog,
        "count": messages.count(),
        "messages_table": MessageTable(messages, request=request),
    }
    return render_to_response("incoming.html", context,
                              context_instance=RequestContext(request))


import csv

def export_to_csv(request):
    # get the response object, this can be used as a stream.
    response = HttpResponse(mimetype='text/csv')
    # force download.
    response['Content-Disposition'] = 'attachment;filename="Messages_log.csv"'

    # the csv writer
    writer = csv.writer(response)

    # just any model...
    messages = Message.objects.select_related('contact',
                                              'connection__backend')

    for message in messages:
        writer.writerow([message.contact, message.connection, message.direction, message.date, message.text])

    return response
