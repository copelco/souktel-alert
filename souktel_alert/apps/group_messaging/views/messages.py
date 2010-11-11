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

from group_messaging.models import Message, Site, Group
from group_messaging.utils import send_message
from group_messaging.forms import MessageTemplateForm


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
def send(request):
    
    messages = Message.objects.all()
    if request.method == 'POST':
        form = SendMessageForm(request.contact.site, request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            date = datetime.now()
            groups = Group.objects.filter(id__in=form.cleaned_data['groups'])
            logging.debug(groups)
            send_message(request.contact, groups, text, date)
            redirect(list)
    else:
        form = SendMessageForm(site=request.contact.site)
    
    context = {'messages': messages, 'form': form}
    
    return render_to_response("messages_send.html", context, context_instance=RequestContext(request))

    
class MessageForm(forms.Form):

    code = forms.CharField(label=_(u"Message code"),max_length=20)
    name = forms.CharField(label=_(u"Message name"),max_length=50)
    text = forms.CharField(label=_(u"Message text"),widget=forms.Textarea(), 
            initial=_(u"Please enter your message here"))


class SendMessageForm(forms.Form):

    def __init__(self, site, *args, **kwargs):
        super(SendMessageForm, self).__init__(*args, **kwargs)

        self.fields['groups'].choices = \
                [(group.id, group.name) for group \
                in Group.objects.filter(active=True, site=site)]
                
    groups = forms.MultipleChoiceField(label=_(u"Groups"))
    text = forms.CharField(label=_(u"Text"),widget=forms.Textarea())
