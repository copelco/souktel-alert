import datetime

from django.db import models
from rapidsms.models import Connection, Contact

class NewsFeed(models.Model):
      
    title = models.CharField(max_length=100,blank=True, null=True)
    description = models.CharField(max_length=500,blank=True, null=True)
    group = models.CharField(max_length=50,blank=True, null=True)
    creator = models.CharField(max_length=50,blank=True, null=True)
    pub_date = models.DateTimeField(null=True, blank=True)
    class Meta:
        get_latest_by = 'pub_date'

