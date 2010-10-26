import datetime

from django.db import models


class NewsFeed(models.Model):
    title = models.CharField(max_length=100,blank=True, null=True)
    description = models.CharField(max_length=200,blank=True, null=True)
    group = models.CharField(max_length=50,blank=True, null=True)
    creator = models.CharField(max_length=50,blank=True, null=True)
    pupdate = models.DateTimeField()
