#!/usr/bin/env python
# encoding=utf-8

from django import forms
from groupmessaging.views.common import webuser_required
from groupmessaging.models import Group
from groupmessaging.models import Site
from groupmessaging.models import Recipient
from groupmessaging.models import WebUser
from rapidsms.webui.utils import render_to_response
from django.http import HttpResponse
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext_lazy as _

class GroupForm(forms.Form):

    def __init__(self, site, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)

        self.fields['recipients'].choices = \
                [(recipient.id, recipient.first_name) for recipient \
                in Recipient.objects.filter(active=True, site=site)]

        self.fields['managers'].choices = \
                [(manager.id, manager.first_name) for manager \
                in WebUser.objects.filter(site=site)]

    code = forms.CharField(label=_(u"Group code"),max_length='15', required=True)
    name = forms.CharField(label=_(u"Group name"),max_length='50', required=True)
    active = forms.BooleanField(label=_(u"active"),required=False)
    recipients = forms.MultipleChoiceField(label=_(u"Group recipients"))
    managers = forms.MultipleChoiceField(label=_(u"Group managers"),required=True)


@webuser_required
def list(request, context):

    ''' List Group '''

    try:
        Site_obj = Site.objects.get(id=context['user'].site.id)
    except Exception, e:
        return HttpResponse("Error 1 : %s" % e)

    try:
        Groups_obj = Group.objects.filter(site=Site_obj)
        paginator = Paginator(Groups_obj,10)

    except Exception, e:
        return HttpResponse("Error 2 : %s" % e)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        Group_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        Group_list = paginator.page(paginator.num_pages)

    mycontext = {'title': 'regyo', 'Glist': Group_list,'count':Groups_obj.count()}
    context.update(mycontext)
    return render_to_response(request, 'groups.html', context)


@webuser_required
def add(request, context):

    ''' add function '''

    if request.method == 'POST':  # If the form has been submitted...
        form = GroupForm(context['user'].site, request.POST)
        if form.is_valid():  # All validation rules pass
            code = form.cleaned_data['code']
            name = form.cleaned_data['name']
            active = form.cleaned_data['active']
            recipients = form.cleaned_data['recipients']
            managers = form.cleaned_data['managers']

            try:
                ins = Group(code=code, name=name,\
                        site=context['user'].site, active=active)
                ins.save()

                for recipient in recipients:
                    ins.recipients.add(recipient)
                for manager in managers:
                    ins.managers.add(manager)

            except Exception, e:
                return HttpResponse("Error 2 : %s" % e)

            return HttpResponseRedirect('/groupmessaging/groups/')

    else:
        form = GroupForm(context['user'].site, {})  # An unbound form
        mycontext = {'form': form}
        context.update(mycontext)

    return render_to_response(request, 'new_group.html', context)


@webuser_required
def delete(request, context, group_id):

    ''' add function '''

    try:
        Groups_obj = Group.objects.get(id=group_id)
        Groups_obj.delete()
    except Exception, e:
        return HttpResponse("Error 2 : %s" % e)

    return redirect(list)


@webuser_required
def update(request, context, group_id):

    ''' add function '''

    if request.method == 'POST':  # If the form has been submitted...
        form = GroupForm(context['user'].site, request.POST)
        if form.is_valid():  # All validation rules pass
            code = form.cleaned_data['code']
            name = form.cleaned_data['name']
            active = form.cleaned_data['active']
            recipients = form.cleaned_data['recipients']
            managers = form.cleaned_data['managers']

            try:
                group = Group.objects.get(id=group_id)
                group.name = name
                group.code = code
                group.active = active
                group.save()

                group.recipients.clear()
                for recipient in recipients:
                    group.recipients.add(recipient)
                group.managers.clear()
                for manager in managers:
                    group.managers.add(manager)
                    
            except Exception, e:
                return HttpResponse("Error 2 : %s" % e)

            return HttpResponseRedirect('/groupmessaging/groups/')
        else:
           return HttpResponse("invalid")
    else:
        Groups_obj = Group.objects.get(id=group_id)
        managers = [(manager.id) for manager \
                    in Groups_obj.managers.select_related()]

        recipients = [(recipient.id) for recipient \
                    in Groups_obj.recipients.select_related()]

        form = GroupForm(context['user'].site, \
                initial={'code': Groups_obj.code, \
                'name': Groups_obj.name, 'active': Groups_obj.active, \
                'managers': managers,'recipients': recipients})

        mycontext = {'form': form, 'group': Groups_obj}
        context.update(mycontext)

    return render_to_response(request, 'update_group.html', context)
