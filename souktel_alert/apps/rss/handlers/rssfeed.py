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
        
        self.respond("This is to get the latest RSS feeds")

    def handle(self, text):        
        try:
            rssfeed = NewsFeed.objects.get(title=text)
        except NewsFeed.DoesNotExist:
            self.respond('There are no feeds')
            return True
        if rssfeed.title:
            self.respond(rssfeed.title)
        else:
            self.respond('No tilte for the feed')
        return True
