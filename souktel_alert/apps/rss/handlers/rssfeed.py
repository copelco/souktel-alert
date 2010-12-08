import datetime

from rapidsms.models import Contact, Connection
from rapidsms.messages import OutgoingMessage
from rapidsms.contrib.scheduler.models import EventSchedule
from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler

#from decisiontree.models import Tree
from rss.models import NewsFeed

class RssHandler(KeywordHandler):

    keyword = "rssfeed"

    def help(self):
        
        self.respond("To get the latest RSS Please send rssfeed l")

    def handle(self, text):        
        feed = NewsFeed.objects.latest()
        self.respond(feed.title)
