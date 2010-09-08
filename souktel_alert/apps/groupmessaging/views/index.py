#!/usr/bin/env python
# encoding=utf-8
import logging

from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from groupmessaging.models import SendingLog, Recipient, Group, OutgoingLog


@login_required
def index(request):
    context = {}
    contact = request.user.get_profile()
    # shortcut
    logging.debug('webuser site: %s' % contact.site)

    # Latest messages (5)
    latest_messages = SendingLog.objects.all()[:5]

    # Statistics
    stats = []

    # Number of recipients
    recipients_num = Recipient.objects.filter(site=contact.site, active=True).count()
    stats.append((_(u"Total Number of Recipients"), recipients_num))

    # Number of groups
    groups_num = Group.objects.filter(site=contact.site, active=True).count()
    stats.append((_(u"Total Number of Groups"), groups_num))

    # Number of messages
    msg_num = SendingLog.objects.filter(sender__site=contact.site).count()
    stats.append((_(u"Total Number of Messages sent"), msg_num))

    # Number of SMS
    sms_num = OutgoingLog.objects.filter(sender__site=contact.site).count()
    stats.append((_(u"Total Number of individual SMS sent"), sms_num))

    mycontext = {'latest_messages': latest_messages, 'stats': stats}
    context = (mycontext)
    return render_to_response('index.html', context,
                              context_instance=RequestContext(request))
