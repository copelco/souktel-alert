import re

from rapidsms.models import Contact, Connection
from rapidsms.messages import OutgoingMessage
from rapidsms.contrib.scheduler.models import EventSchedule
from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler


new_re = re.compile(r'\w+')
answer_re = re.compile(r'\d+')
active_re = re.compile(r'^active$')


class GoalHandler(KeywordHandler):

    keyword = "goal"

    def help(self):
        self.respond("To echo some text, send: ECHO <ANYTHING>")

    def handle(self, text):
        connection = self.msg.connection
        identity = connection.identity
        try:
            contact = Contact.objects.filter(connection__identity=identity)[0]
        except IndexError:
            self.warning('{0} is unrecognized'.format(connection))
            self.respond('You must register before using the goals app')
            return True
        connection.contact = contact
        connection.save()
        if answer_re.match(text):
            return self._handle_answer(text, connection.contact)
        if active_re.match(text):
            return self._handle_active(text, connection.contact)
        elif new_re.match(text):
            return self._handle_new(text, connection.contact)

    def _handle_new(self, text, contact):
        contact.goals.create(body=text, contact=self.msg.connection.contact)
        self.respond('Your goal has been recorded.')

    def _handle_active(self, text, contact):
        try:
            complete_goals = contact.goals.filter(complete=False)
            goal = complete_goals.order_by('date_last_notified')[0]
        except IndexError:
            self.respond('All of your goals are complete')
        contact.goals.update(in_session=False)
        goal.in_session = True
        goal.save()
        template = """You stated that your goal was "%(goal)s". Please reply with a number between 1 and 5. Thanks!"""
        self.respond(template, goal=goal)

    def _handle_answer(self, text, contact):
        try:
            goal = contact.goals.filter(in_session=True)[0]
        except IndexError:
            self.warning('No goal sessions found for {0}'.format(contact))
            goal = None
        if goal:
            goal.answers.create(body=text)
            goal.in_session = False
            goal.complete = True
            goal.save()
            response = 'Thank you for your response!'
        else:
            response = "You don't currently have any open goal sessions"
        self.respond(response)
        return True
