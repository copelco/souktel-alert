#!/usr/bin/env python
# encoding=utf-8
import logging
from datetime import datetime

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from group_messaging.models import Message, Site, Group
from group_messaging.forms import MessageTemplateForm, SendMessageForm


@login_required
def list(request):
    context = {
        'templates': Message.objects.order_by('name'),
    }
    return render_to_response('messages/list.html', context,
                              context_instance=RequestContext(request))


@login_required
@transaction.commit_on_success
def messageform(request, messageid=None):
    message = None
    if messageid:
           message = get_object_or_404(Message, pk=messageid)
    if request.method == 'POST':
        form = MessageTemplateForm(request.POST, instance=message)
        if form.is_valid():
            user = form.save()
            messages.info(request, "Message saved successfully")
            return HttpResponseRedirect(reverse('messages_list'))
    else:
        form = MessageTemplateForm(instance=message)
    context = {
        'message': message,
        'form': form,
    }
    return render_to_response('messages/create_edit.html', context,
                              context_instance=RequestContext(request))


@login_required
@transaction.commit_on_success
def delete(request, messageid):
    message = get_object_or_404(Message, pk=messageid)
    message.delete()
    messages.info(request, "Message deleted successfully")
    return HttpResponseRedirect(reverse('messages_list'))


@login_required
@transaction.commit_on_success
def send(request):
    if request.method == 'POST':
        form = SendMessageForm(request.POST)
        if form.is_valid():
            form.send_message(request.contact)
            messages.info(request, "Message queued for delivery")
            return HttpResponseRedirect(reverse('messages_list'))
    else:
        form = SendMessageForm()
    templates = {}
    for pk, text in Message.objects.values_list('id', 'text'):
        templates[pk] = text
    context = {
        'templates': json.dumps(templates),
        'form': form,
    }
    return render_to_response("messages/send.html", context,
                              context_instance=RequestContext(request))

