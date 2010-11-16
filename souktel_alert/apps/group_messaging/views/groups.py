#!/usr/bin/env python
# encoding=utf-8
import logging

from django import forms
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages

from rapidsms.models import Contact

from group_messaging.models import Group, Site
from group_messaging.forms import GroupForm


@login_required
def list(request):
    groups = Group.objects.annotate(count=Count('recipients'))
    context = {
        'groups': groups.order_by('code'),
    }
    return render_to_response('groups_users/groups/list.html', context,
                              context_instance=RequestContext(request))


@login_required
def create_edit_group(request, group_id=None):
    group = None
    if group_id:
        group = get_object_or_404(Group, pk=group_id)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.info(request, "Group saved successfully")
            return HttpResponseRedirect(reverse('groups'))
    else:
        form = GroupForm(instance=group)
    context = {
        'form': form,
        'group': group,
    }
    return render_to_response('groups_users/groups/create_edit.html', context,
                              context_instance=RequestContext(request))


@login_required
@transaction.commit_on_success
def delete(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    group.delete()
    messages.info(request, 'Group successfully deleted')
    return HttpResponseRedirect(reverse('groups'))

