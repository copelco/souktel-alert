import re
import datetime

from rapidsms.models import Contact, Connection
from rapidsms.messages import OutgoingMessage
from rapidsms.contrib.scheduler.models import EventSchedule
from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler


new_re = re.compile(r'\w+')
answer_re = re.compile(r'\d+')
active_re = re.compile(r'^next$')
close_re = re.compile(r'^close$')


class GoalHandler(KeywordHandler):

    keyword = "goal"

    def help(self):
        self.respond("To echo some text, send: ECHO <ANYTHING>")

    def handle(self, text):
        connection = self.msg.connection
        identity = connection.identity
        try:
            Contact.objects.filter(connection__identity=identity)[0]
        except IndexError:
            self.warning('{0} is unrecognized'.format(connection))
            self.respond('You must register before using the goals app')
            return True
        if answer_re.match(text):
            return self._handle_answer(text, connection.contact)
        elif active_re.match(text):
            return self._handle_active(text, connection.contact)
        elif close_re.match(text):
            return self._handle_close(text, connection.contact)
        elif new_re.match(text):
            return self._handle_new(text, connection.contact)

    def _handle_new(self, text, contact):
        contact.goals.create(body=text, contact=self.msg.connection.contact)
        self.respond('Your goal has been recorded.')

    def _handle_active(self, text, contact):    
        complete_goals = contact.goals.filter(complete=False)
        try:
            goal = complete_goals.order_by('date_last_notified')[0]
        except IndexError:
            self.respond('All of your goals are complete')
        # close all other sessions
        contact.goals.update(in_session=False)
        goal.in_session = True
        goal.date_last_notified = datetime.datetime.now()
        goal.save()
        month = goal.date_created.strftime('%b')
        from goals.app import GoalsApp
        self.respond(GoalsApp.template, month=month, goal=goal)

    def _handle_close(self, text, contact):    
        try:
            goal = contact.goals.filter(complete=False, in_session=True)[0]
        except IndexError:
            self.respond('No goals to close')
        goal.in_session = False
        goal.complete = True
        goal.save()
        self.respond('Goal "%(goal)s" closed', goal=goal)

    def _handle_answer(self, text, contact):
        try:
            goal = contact.goals.filter(in_session=True, complete=False)[0]
        except IndexError:
            self.warning('No goal sessions found for {0}'.format(contact))
            goal = None
        if goal:
            goal.answers.create(body=text)
            goal.in_session = False
            goal.save()
            response = 'Thank you for your response!'
        else:
            response = "You don't currently have any open goal sessions"
        self.respond(response)
        return True
