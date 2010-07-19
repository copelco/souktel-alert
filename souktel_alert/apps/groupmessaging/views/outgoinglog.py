#!/usr/bin/env python
# encoding=utf-8

from django.http import HttpResponseRedirect
from rapidsms.webui.utils import render_to_response
from groupmessaging.models import OutgoingLog

from groupmessaging.views.common import webuser_required
from django import forms
from django.shortcuts import redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext_lazy as _


@webuser_required
def list(request, context):
    
    outgoinglog = OutgoingLog.objects.all()
    paginator = Paginator(outgoinglog,10)
    
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    
    try:
        outgoinglog_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        outgoinglog_list = paginator.page(paginator.num_pages)


    mycontext = {'outgoinglog': outgoinglog_list,'form':LogForm() , 'logs':outgoinglog , 'count':outgoinglog.count()}
    context.update(mycontext)
    return render_to_response(request, 'outgoing_log.html', context)


@webuser_required
def filter(request, context):
   
    outgoinglog_list=""
    form =""
    outgoinglog=""
    statusMsg=""
    senderMsg=""
    identityMsg=""
    textMsg=""
    outgoinglog2=""
    #if request.method == 'POST':
    form = LogForm(request.POST)

    if form.is_valid():
            statusMsg = form.cleaned_data['status']
           # senderMsg = form.cleaned_data['sender']
           # identityMsg  = form.cleaned_data['identity']
           # textMsg  = form.cleaned_data['text']

    else:
             print "form is not valid"


    outgoinglog = OutgoingLog.objects.filter(status=statusMsg)
    outgoinglog2 = OutgoingLog.objects.all()
    paginator = Paginator(outgoinglog,10)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        outgoinglog_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        outgoinglog_list = paginator.page(paginator.num_pages)
     
    mycontext = {'outgoinglog': outgoinglog_list,'form':form ,'count':0,'logs':outgoinglog2}
    context.update(mycontext)
    return render_to_response(request, 'outgoing_log.html', context )

class LogForm(forms.Form):

    #pass
    #sender = forms.CharField(label=_(u"Sender"), max_length=50)
    #identity  = forms.CharField(label=_(u"Identity"),max_length=50)
     #text  = forms.CharField(label=_(u"text"),max_length=30)
     status    = forms.CharField(label=_(u"Status"),required=False)
    #site      = forms.ModelMultipleChoiceField(queryset= Site.objects.all(), required=True)




   
