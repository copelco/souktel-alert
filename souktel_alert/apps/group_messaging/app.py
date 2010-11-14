#!/usr/bin/env python
# encoding=utf-8

import rapidsms
from rapidsms.contrib.scheduler.models import EventSchedule
from rapidsms.apps.base import AppBase

from django.utils.translation import ugettext as _
from django.template import RequestContext

from parsers.keyworder import Keyworder

from group_messaging.utils import *


def loop2mn(loop):
    ''' Generates an array of numbers for Event Schudule minutes '''

    try:
        loop = int(loop)
    except:
        loop = 1

    mn = []
    for num in range(0,60):
        if num % loop == 0:
            mn.append(num)
    return 10


def scheduler_callback(router):
    app = router.get_app("group_messaging")
    app.send_messages()


class App(AppBase):

    keyword = Keyworder()
    cron_schedule = {'minutes': '*'}
    cron_name = 'messaging-cron-job'
    cron_callback = 'group_messaging.app.scheduler_callback'

    def configure(self, interval=1, *args, **kwargs):
        self.log.debug('configure')
        # convert (and store) minutes from config
        self.minutes = loop2mn(interval)

    def start(self):
        try:
            schedule = EventSchedule.objects.get(description=self.name)
        except EventSchedule.DoesNotExist:
            schedule = EventSchedule.objects.create(description=self.name,
                                                    callback=self.cron_callback,
                                                    minutes='*')
        schedule.callback = self.cron_callback
        for key, val in self.cron_schedule.iteritems():
            if hasattr(schedule, key):
                setattr(schedule, key, val)
        schedule.save()
        self.info('started')

    def send_messages(self):
        self.debug('{0} running'.format(self.cron_name))
        messages = OutgoingLog.objects.filter(status=OutgoingLog.QUEUED)[:10]
        self.info('found {0} messages'.format(messages.count()))
        for message in messages:
            recipient = message.recipient.default_connection
            msg = OutgoingMessage(connection=recipient, template=message.text)
            success = True
            try:
                msg.send()
            except Exception, e:
                self.exception(e)
                success = False
            if success:
                message.status = str(OutgoingLog.DELIVERED)
            else:
                message.status = str(OutgoingLog.FAILED)
            message.save()

    def handle(self, message):
        
        try:
            func, captures = self.keyword.match(self, message.text)
        except TypeError:
            self.debug('not captured')
            return False

        try:
            return func(self, message, *captures)
        except Exception, e:
            self.exception(e)
            message.respond('An error has occurred.')
            return False

    keyword.prefix = ['queue']
    @keyword('')
    def queue(self, message):
        message.respond(_(u"Launching queue..."))
        self.debug("Launching queue...")
        process_queue(self.router)
        message.respond(_(u"Queue processed"))

