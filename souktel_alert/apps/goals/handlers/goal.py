import re

from rapidsms.models import Contact, Connection
from rapidsms.messages import OutgoingMessage
from rapidsms.contrib.scheduler.models import EventSchedule
from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler


new_re = re.compile(r'\w+')
answer_re = re.compile(r'\d+')


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
            self.warning('{0} is unrecognized')
            contact = None
        if contact:
            # associate connection to contact for later use
            connection.contact = contact
            connection.save()
        if answer_re.match(text):
            return self._handle_answer(text)
        elif new_re.match(text):
            return self._handle_new(text)

    def _handle_new(self, text):
        contact = self.msg.connection.contact
        contact.goals.create(body=text, contact=self.msg.connection.contact)
        self.respond('Your goal has been recorded.')

    def _handle_answer(self, text):
        contact = self.msg.connection.contact
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
        msg = OutgoingMessage(connection=self.msg.connection,
                              template=response)
        msg.send()
        return True
