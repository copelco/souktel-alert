#!/usr/bin/env python
# encoding=utf-8

from rapidsms.webui.utils import render_to_response
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from groupmessaging.views.common import webuser_required
from groupmessaging.models import SendingLog, Recipient, Group, OutgoingLog


@webuser_required
def index(request, context):

    # shortcut
    webuser = context['user']
    print webuser.site

    # Latest messages (5)
    latest_messages = SendingLog.objects.all()[:5]

    # Statistics
    stats = []

    # Number of recipients
    recipients_num = Recipient.objects.filter(site=webuser.site, active=True).count()
    stats.append((_(u"Total Number of Recipients"), recipients_num))

    # Number of groups
    groups_num = Group.objects.filter(site=webuser.site, active=True).count()
    stats.append((_(u"Total Number of Groups"), groups_num))

    # Number of messages
    msg_num = SendingLog.objects.filter(sender__site=webuser.site).count()
    stats.append((_(u"Total Number of Messages sent"), msg_num))

    # Number of SMS
    sms_num = OutgoingLog.objects.filter(sender__site=webuser.site).count()
    stats.append((_(u"Total Number of individual SMS sent"), sms_num))

    mycontext = {'latest_messages': latest_messages, 'stats': stats}
    context.update(mycontext)
    return render_to_response(request, 'index.html', context)
