#!/usr/bin/env python
# encoding=utf-8

from datetime import datetime

from groupmessaging.models import SendingLog, OutgoingLog

def process_queue_callback(router, *args, **kwargs):
    return process_queue(router)

def process_queue(router):

    # queued messages
    messages = OutgoingLog.objects.filter(status=OutgoingLog.QUEUED)[:10]

    for message in messages:

        # loop on recipients
        back = None

        for backend in router.backends:
            if hasattr(backend, 'slug') and backend.slug == message.backend \
               or hasattr(backend, 'type') and backend.type == message.backend:
                back = backend

        if not back:
            message.status = message.FAILED
            message.save()
            continue

        # create message object
        try:
            msg = back.message(message.identity, message.text)
            msg.send()
            message.status = message.PENDING
            message.sent_on = datetime.now()
            message.save()
        except:
            message.status = message.FAILED
            message.save()

def send_message(sender, groups, text, date):
    
    # create message object
    message = SendingLog(sender=sender, text=text, date=date)
    message.save()

    # attach groups
    for group in groups:

        # skip non-active groups
        if not group.active:
                continue
        message.groups.add(group)

        # attach recipients from group
        for recipient in group.recipients.select_related():

            # skip non-active recipients
            if not recipient.active:
                continue

            message.recipients.add(recipient)

            # create to-send messages
            msg = OutgoingLog(sender=sender, identity=recipient.identity, \
                              backend=recipient.backend, text=message.text, \
                              status=OutgoingLog.QUEUED)
            msg.save()
    
