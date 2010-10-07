import datetime

from rapidsms.models import Contact, Connection
from rapidsms.messages import OutgoingMessage
from rapidsms.contrib.scheduler.models import EventSchedule
from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler

from decisiontree.models import Tree


class ResultsHandler(KeywordHandler):

    keyword = "results"

    def help(self):
        self.respond("Please enter a survey keyword")

    def handle(self, text):
        try:
            tree = Tree.objects.get(trigger=text)
        except Tree.DoesNotExist:
            self.respond('Survey "%s" does not exist' % text)
            return True
        if tree.summary:
            self.respond(tree.summary.replace('%', '%%'))
        else:
            self.respond('No summary for "%s" survey' % text)
        return True
