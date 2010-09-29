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
from group_messaging.forms import logFilter



@contact_required
def list(request):
    
    outgoinglog = OutgoingLog.objects.all()
    messagelog = logFilter(request.GET, queryset=OutgoingLog.objects.all())
    
    mycontext = {'messagelog': messagelog,'count':outgoinglog.count()}
    context = (mycontext)
    return render_to_response('filter.html', context, context_instance=RequestContext(request))

#@contact_required
#def log_search(request):
    
 #   log = logFilter(request.GET, queryset=OutgoingLog.objects.all())
  #  return render_to_response('filter.html', {'log': log  ,'list': list})



   
