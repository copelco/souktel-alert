#!/usr/bin/env python
# encoding=utf-8
import logging
from datetime import datetime

from rapidsms.models import Connection, Backend
from rapidsms.messages.outgoing import OutgoingMessage

from group_messaging.models import SendingLog, OutgoingLog


logger = logging.getLogger(__name__)


def process_queue_callback(router, *args, **kwargs):
    return process_queue(router)


def process_queue(router):
    logger.debug('processing queue')
    # queued messages
    messages = OutgoingLog.objects.filter(status=OutgoingLog.QUEUED)[:10]

    for message in messages:
        logger.debug('Processing message: %s', message)
        
        conn, _ = Connection.objects.get_or_create(identity=message.identity,
                                                   backend=message.backend)
        msg = OutgoingMessage(conn, message.text)
        msg.send()
        message.status = str(OutgoingLog.DELIVERED)
        message.save()

