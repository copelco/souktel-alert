import urllib, os, time, datetime, feedparser

from django.shortcuts import redirect, render_to_response, get_object_or_404
from django import forms
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.contrib.auth.decorators import login_required

def summary(request, posts_to_show=5):
    feed_url = 'http://news.google.com/news?ned=us&topic=h&output=rss'
    
    feed = feedparser.parse(feed_url)
    posts = []
    for i in range(posts_to_show):
        pub_date = feed['entries'][i].updated_parsed
        published = datetime.date(pub_date[0], pub_date[1], pub_date[2] )
        #print feed['entries'][i].title
        posts.append({
            'title': feed['entries'][i].title,
            'summary': feed['entries'][i].summary,
            'link': feed['entries'][i].link,
            'date': published,
        })
    #return {'posts': posts}

    context = {'posts': posts}
    return render_to_response('summary.html', context,
                              context_instance=RequestContext(request))
