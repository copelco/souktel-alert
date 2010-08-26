from rapidsms.contrib.scheduler.models import EventSchedule
from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler


class GoalHandler(KeywordHandler):

    keyword = "goal"

    def help(self):
        self.respond("To echo some text, send: ECHO <ANYTHING>")

    def handle(self, text):
        from goals.models import Goal
        connection = self.msg.connection
        # disable previous goals
        Goal.objects.filter(connection=connection).update(active=False)
        goal = Goal.objects.create(connection=connection, body=text)
        self.respond('Your goal has been recorded.')
