#!/usr/bin/env python
# encoding=utf-8

import rapidsms
from rapidsms.parsers.keyworder import Keyworder
from django.utils.translation import ugettext as _
from scheduler.models import EventSchedule

from groupmessaging.utils import *

def loop2mn(loop):
    ''' Generates an array of numbers for Event Schudule minutes '''

    try:
        loop = int(loop)
    except:
        loop = 5

    mn = []
    for num in range(0,60):
        if num % loop == 0:
            mn.append(num)
    return mn


class App(rapidsms.app.App):

    keyword = Keyworder()

    def configure(self, interval=5, *args, **kwargs):

        # convert (and store) minutes from config
        self.minutes = loop2mn(interval)

    def start(self):

        # create a scheduled event if not present
        # due to bug in fixture handling in scheduler
        event_desc = 'groupmessaging_main'
        if EventSchedule.objects.filter(description=event_desc).count() > 0:
            return

        schedule = EventSchedule(description=event_desc, \
                     callback="groupmessaging.utils.process_queue_callback", \
                     minutes=self.minutes, \
                     callback_args=('self.router'))
        schedule.save()
        self.log('DEBUG', u"Created Event Schedule %s" % event_desc)

    def handle(self, message):
        
        try:
            func, captures = self.keyword.match(self, message.text)
        except TypeError:
            self.log('DEBUG', 'not captured')
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
        process_queue(self.router)
        message.respond(_(u"Queue processed"))
