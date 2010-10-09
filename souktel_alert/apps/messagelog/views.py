#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from .tables import MessageTable
from .models import Message


@login_required
def message_log(req):
    return render_to_response(
        "messagelog/index.html", {
            "messages_table": MessageTable(Message.objects.all(), request=req)
        }, context_instance=RequestContext(req)
    )
