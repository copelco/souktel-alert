from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler


class GoalHandler(KeywordHandler):

    keyword = "goal"

    def help(self):
        self.respond("To echo some text, send: ECHO <ANYTHING>")

    def handle(self, text):
        from goals.models import Goal
        goal = Goal.objects.create(connection=self.msg.connection, body=text)
        self.respond('Your goal has been recorded.')
