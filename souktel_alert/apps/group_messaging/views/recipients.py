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
from django.contrib.auth.models import User
from django.db.models import Count
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseRedirect

from rapidsms.models import Contact, Connection, Backend

from group_messaging.models import Site, Group

from group_messaging.forms import RecipientForm, ConnectionFormset,\
                                  CSVUploadForm, UserForm


logger = logging.getLogger(__file__)


@login_required
def list_recipients(request):
    identity_map = {}
    for connection in Connection.objects.exclude(contact__isnull=True):
        if connection.contact_id not in identity_map:
            identity_map[connection.contact_id] = set()
        identity_map[connection.contact_id].add(connection.identity)
    recipients = Contact.objects.annotate(count=Count('group_recipients'))
    recipients = recipients.order_by('last_name', 'first_name')
    for recipient in recipients:
        recipient.identities = identity_map.get(recipient.pk, set())
    context = {
        'recipients': recipients,
    }
    return render_to_response('groups_users/recipients/list.html', context,
                              context_instance=RequestContext(request))


@login_required
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
    return render_to_response('groups_users/recipients/create_edit.html', context,
                              context_instance=RequestContext(request))


@login_required
def delete(request, recipientid):
    recipient = get_object_or_404(Contact, pk=recipientid)
    recipient.delete()
    msg = "You have successfully deleted this record"
    messages.add_message(request, messages.INFO, msg)
    return HttpResponseRedirect(reverse('list_recipients'))


@login_required
@transaction.commit_manually
def manage_recipients(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            backend = Backend.objects.get(name='javna')
            rows = form.save()
            for row in rows:
                first_name = row[0]
                last_name = row[1]
                identity = row[2]
                country = row[3]
                city = row[4]
                age = row[5]
                gender = row[6]
                comment = row[7]
                contact, created = Contact.objects.get_or_create(
                    first_name=first_name,
                    last_name=last_name
                )
                if created:
                    contact.country = country
                    contact.city = city
                    contact.age = age
                    contact.gender = gender
                    contact.comment = comment
                    try:
                        contact.save()
                    except Exception, e:
                        transaction.rollback()
                        logger.exception(e)
                        msg = "CSV import failed: %s" % e
                        messages.error(request, msg)
                        return HttpResponseRedirect(reverse('manage_recipients'))
                if form.cleaned_data['group']:
                    contact.group_recipients.add(form.cleaned_data['group'])
                conn, _ = Connection.objects.get_or_create(identity=identity,
                                                           backend=backend)
                conn.contact = contact
                conn.save()
            transaction.commit()
            msg = "Import successful"
            messages.info(request, msg)
            return HttpResponseRedirect(reverse('list_recipients'))

    else:
        form = CSVUploadForm()
    context = {
        'form': form,
    }
    return render_to_response('groups_users/recipients/csv.html', context,
                              context_instance=RequestContext(request))



@login_required
def list_users(request):
    context = {
      'users': User.objects.order_by('username'),
    }
    return render_to_response('groups_users/users/list.html', context,
                              context_instance=RequestContext(request))


@login_required
@transaction.commit_on_success
def create_edit_user(request, user_id=None):
    user = None
    if user_id:
           user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.info(request, "User saved successfully")
            return HttpResponseRedirect(reverse('list_users'))
    else:
        form = UserForm(instance=user)
    context = {
        'user': user,
        'form': form,
    }
    return render_to_response('groups_users/users/create_edit.html', context,
                              context_instance=RequestContext(request))


@login_required
@transaction.commit_on_success
def delete_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    messages.info(request, 'User successfully deleted')
    return HttpResponseRedirect(reverse('list_users'))
