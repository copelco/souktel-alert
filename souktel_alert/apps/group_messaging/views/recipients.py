#!/usr/bin/env python
# encoding=utf-8
import logging

from django import forms
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext
from django.forms.formsets import formset_factory
from django.contrib import messages
from django.db import transaction
from django.core.urlresolvers import reverse

from django.http import HttpResponseRedirect

from rapidsms.models import Contact, Connection, Backend

from group_messaging.models import Recipient
from group_messaging.models import Site
from group_messaging.models import Group
from group_messaging.decorators import contact_required

from group_messaging.forms import RecipientForm, ConnectionFormset,\
                                  CSVUploadForm


@contact_required
def list_recipients(request):
    recipients = Contact.objects.all()
    paginator = Paginator(recipients,10)
    
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    
    try:
        recipient_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        recipient_list = paginator.page(paginator.num_pages)

    context = {'recipients': recipient_list,'count':recipients.count()}
    return render_to_response('recipients_list.html', context,
                              context_instance=RequestContext(request))


@contact_required
@transaction.commit_on_success
def recipient(request, recipientid=None):
    instance = Contact()
    if recipientid:
        instance = get_object_or_404(Contact, pk=recipientid)

    if request.method == 'POST':
        form = RecipientForm(request.POST, instance=instance)
        formset = ConnectionFormset(request.POST, instance=instance)
        if form.is_valid() and formset.is_valid():
            saved_contact = form.save()
            connections = formset.save(commit=False)
            for connection in connections:
                connection.contact = saved_contact
                connection.save()
            if recipientid:
                msg = _(u"You have successfully updated the recipient")
            else:
                msg = "You have successfully inserted a recipient %s."
                msg = _(msg % saved_contact.name)
            messages.info(request, msg)
            return HttpResponseRedirect(reverse('list_recipients'))
    else:
        form = RecipientForm(instance=instance)
        formset = ConnectionFormset(instance=instance)

    context = {
        'recipient': recipient,
        'form': form,
        'formset': formset,
    }
    return render_to_response('recipient.html', context,
                              context_instance=RequestContext(request))


@contact_required
def delete(request, recipientid):
    recipient = get_object_or_404(Contact, pk=recipientid)
    recipient.delete()
    msg = "You have successfully deleted this record"
    messages.add_message(request, messages.INFO, msg)
    return redirect(list_recipients)


class BulkRecipientForm(forms.Form):
       
    firstName = forms.CharField(label=_(u"First Name"), max_length=50)
    lastName  = forms.CharField(label=_(u"Last Name"),max_length=50)
    identity  = forms.CharField(label=_(u"Identity"),max_length=30)
    active    = forms.BooleanField(label=_(u"Active"),required=False)


@contact_required
@transaction.commit_on_success
def manage_recipients(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            backend = Backend.objects.get(name='javna')
            rows = form.save()
            for row in rows:
                first_name, last_name, identity = row
                contact, _ = Contact.objects.get_or_create(first_name=first_name,
                                                           last_name=last_name)
                conn, _ = Connection.objects.get_or_create(identity=identity,
                                                           backend=backend)
                conn.contact = contact
                conn.save()
            msg = "Import successful"
            messages.info(request, msg)
            return HttpResponseRedirect(reverse('recipients_list'))

    else:
        form = CSVUploadForm()
    context = {
        'form': form,
    }
    return render_to_response('manage_recipients.html', context,
                              context_instance=RequestContext(request))
