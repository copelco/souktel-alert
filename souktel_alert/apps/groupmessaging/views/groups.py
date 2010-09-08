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
from django.contrib.auth.decorators import login_required

from rapidsms.models import Contact

from groupmessaging.models import Group, Site, Recipient


class GroupForm(forms.Form):

    def __init__(self, site, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)

        self.fields['recipients'].choices = \
                [(recipient.id, recipient.first_name) for recipient \
                in Recipient.objects.filter(active=True, site=site)]

        self.fields['managers'].choices = \
                [(manager.id, manager.user.first_name) for manager \
                in Contact.objects.filter(site=site)]
    
    # logging.debug('webuser : %s' % WebUser)
              
    code = forms.CharField(label=_(u"Group code"),max_length='15', required=True)
    name = forms.CharField(label=_(u"Group name"),max_length='50', required=True)
    active = forms.BooleanField(label=_(u"active"),required=False)
    recipients = forms.MultipleChoiceField(label=_(u"Group recipients"))
    managers = forms.MultipleChoiceField(label=_(u"Group managers"),required=True)
    

@login_required
def list(request):
    contact = request.user.get_profile()
    ''' List Group '''

    try:
        Site_obj = Site.objects.get(id=contact.site.id)
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

    context = {'title': 'regyo', 'Glist': Group_list,'count':Groups_obj.count()}
    return render_to_response('groups.html', context, context_instance=RequestContext(request))


@login_required
def add(request):
    ''' add function '''

    if request.method == 'POST':  # If the form has been submitted...
        form = GroupForm(request.contact.site, request.POST)
        if form.is_valid():  # All validation rules pass
            code = form.cleaned_data['code']
            name = form.cleaned_data['name']
            active = form.cleaned_data['active']
            recipients = form.cleaned_data['recipients']
            managers = form.cleaned_data['managers']
           
            
            try:
                ins = Group(code=code, name=name,\
                        site=request.contact.site, active=active)
                ins.save()

                for recipient in recipients:
                    ins.recipients.add(recipient)
                for manager in managers:
                    ins.managers.add(manager)
                

            except Exception, e:
                return HttpResponse("Error 2 : %s" % e)

            return HttpResponseRedirect('/groupmessaging/groups/')

    else:
        form = GroupForm(site=request.contact.site)  # An unbound form
        context = {'form': form}

    return render_to_response('new_group.html', context, context_instance=RequestContext(request))


@login_required
def delete(request, group_id):

    ''' add function '''

    try:
        Groups_obj = Group.objects.get(id=group_id)
        Groups_obj.delete()
    except Exception, e:
        return HttpResponse("Error 2 : %s" % e)

    return redirect(list)


@login_required
def update(request, group_id):
    group = get_object_or_404(Group, pk=group_id)

    ''' add function '''
    if request.method == 'POST':  # If the form has been submitted...
        form = GroupForm(request.contact.site, request.POST)
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
        Groups_obj = Group.objects.get(id=group_id)
        managers = [(manager.id) for manager \
                    in Groups_obj.managers.select_related()]

        recipients = [(recipient.id) for recipient \
                    in Groups_obj.recipients.select_related()]

        form = GroupForm(request.contact.site, \
                initial={'code': Groups_obj.code, \
                'name': Groups_obj.name, 'active': Groups_obj.active, \
                'managers': managers,'recipients': recipients})

    context = {'form': form, 'group': group}

    return render_to_response('update_group.html', context, context_instance=RequestContext(request))
