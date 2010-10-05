#!/usr/bin/env python
# encoding=utf-8
import logging
from datetime import datetime

from django import forms
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from group_messaging.decorators import contact_required
from group_messaging.models import Message, Site, Group
from group_messaging.utils import send_message



@contact_required
def list(request):
    ''' List all the Messages'''
    messages = Message.objects.all()
    count = Message.objects.count()
    mycontext = {'messages': messages, 'count': count}
    context = (mycontext)

    return render_to_response('messages.html', context, context_instance=RequestContext(request))


@contact_required
def messageform(request, messageid=None):
    '''form for Add/Edit messages'''
    if not messageid or int(messageid) == 0:
        mess = None
    else:
        mess = Message.objects.get(id=messageid)
        
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            if mess:         
  
                mess.code = form.cleaned_data['code']
                mess.name = form.cleaned_data['name']
                mess.text = form.cleaned_data['text']
                mess.site = request.contact.site
                mess.save()
                                
            else: 
            
                mess = Message(code=form.cleaned_data['code'],\
                                           name=form.cleaned_data['name'],\
                                            text=form.cleaned_data['text'],\
                                            site=request.contact.site)           
                mess.save()
                mess = Message.objects.all()
                mycontext = {'mess': mess}
                context = (mycontext)
                return redirect(list)
           
    else:
        if mess:
            data = {'name': mess.name, 'text': mess.text, 'code': mess.code}          
        else:
            data = {'code': '', 'name': '', 'test': ''}
        form = MessageForm(data) 
            
    if not messageid:
        messageid = 0
    
    mycontext = {'mess': mess, 'form': form, 'messageid': messageid}
    context = (mycontext)
    return render_to_response("messages_form.html", context, context_instance=RequestContext(request))


@contact_required    
def delete(request, messageid):
    
    message = Message.objects.get(id=messageid)
    message.delete()
    mycontext = {'message': message}
    context = (mycontext)
       
    return redirect(list)


@contact_required
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
