#!/usr/bin/env python
# encoding=utf-8

import rapidsms
from parsers.keyworder import Keyworder
from django.utils.translation import ugettext as _
from rapidsms.contrib.scheduler.models import EventSchedule
from rapidsms.apps.base import AppBase
from django.template import RequestContext

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


class App(AppBase):

    keyword = Keyworder()

    def configure(self, interval=1, *args, **kwargs):
        self.log.debug('configure')
        # convert (and store) minutes from config
        self.minutes = loop2mn(interval)

    def start(self):

        # create a scheduled event if not present
        # due to bug in fixture handling in scheduler
        event_desc = 'group_messaging_main'
        if EventSchedule.objects.filter(description=event_desc).count() > 0:
            return

        schedule = EventSchedule(description=event_desc, \
                     callback="group_messaging.utils.process_queue_callback", \
		     minutes=([00,58]), \
                     callback_args=('self.router'))
        schedule.save()
        self.debug(u"Created Event Schedule %s" % event_desc)

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
