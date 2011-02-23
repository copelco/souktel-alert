import urllib, os, time, datetime, feedparser

from django.shortcuts import redirect, render_to_response, get_object_or_404
from django import forms
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.contrib.auth.decorators import login_required


from rss.models import NewsFeed

def summary(request, posts_to_show=2):

    # Feed url to fecth the RSS feeds from TWB
    feed_url = "http://www.python.org/cgi-bin/moinmoin/RecentChanges?action=rss_rc"
    
    feed = feedparser.parse(feed_url)
    
    #feed2 = NewsFeed.
    #feed2.save()
    posts = []
    for i in range(posts_to_show):
        pub_date = feed['entries'][i].updated_parsed
        published = datetime.date(pub_date[0], pub_date[1], pub_date[2] )
        
        posts.append({
            'title': feed['entries'][i].title,
            'summary': feed['entries'][i].summary,
            'link': feed['entries'][i].link,
            'date': published,
        })
       
    feed2 = NewsFeed(title=feed['entries'][i].title,\
    description=feed['entries'][i].summary,group=feed['entries'][i].group,pub_date=published)
    #feed2 = NewsFeed(description=feed['entries'][i].summary)
    #feed2 = NewsFeed(group=feed['entries'][i].group)
    #feed2 = NewsFeed(group=published)
    feed2.save()
    context = {'posts': posts}
    return render_to_response('summary.html', context,
                              context_instance=RequestContext(request))
