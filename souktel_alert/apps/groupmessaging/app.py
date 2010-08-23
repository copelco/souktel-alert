#!/usr/bin/env python
# encoding=utf-8

import rapidsms
import logging
from rapidsms.parsers.keyworder import Keyworder
from django.utils.translation import ugettext as _
from rapidsms.contrib.scheduler.models import EventSchedule
from rapidsms.apps.base import AppBase
from django.template import RequestContext

from groupmessaging.utils import *

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
    return mn


class App(AppBase):

    keyword = Keyworder()

    def configure(self, interval=1, *args, **kwargs):
        self.log.debug('configure')
        # convert (and store) minutes from config
        self.minutes = loop2mn(interval)

    def start(self):

        # create a scheduled event if not present
        # due to bug in fixture handling in scheduler
        logging.DEBUG("Start")
        event_desc = 'groupmessaging_main'
        if EventSchedule.objects.filter(description=event_desc).count() > 0:
            return

        schedule = EventSchedule(description=event_desc, \
                     callback="groupmessaging.utils.process_queue_callback", \
		     minutes=([00,60]), \
                     callback_args=('self.router'))
        schedule.save()
        loggin.DEBUG(u"Created Event Schedule %s" % event_desc)

    def handle(self, message):
        
        try:
            func, captures = self.keyword.match(self, message.text)
        except TypeError:
            loggin.DEBUG('not captured')
            return False

        try:
            return func(self, message, *captures)
        except Exception, e:
            message.respond(_(u"System Error: %s") % e)
            return True

    keyword.prefix = ['queue']
    @keyword('')
    def queue(self, message):
        message.respond(_(u"Launching queue..."))
        loggin.DEBUG("Launching queue...")
        process_queue(self.router)
        message.respond(_(u"Queue processed"))
