import datetime

from django.db import models

from rapidsms.models import Connection, Contact


class Goal(models.Model):
    connection = models.ForeignKey(Connection)
    date_created = models.DateTimeField()
    date_last_notified = models.DateTimeField()
    body = models.TextField()
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.body

    def save(self, **kwargs):
        if not self.pk:
            self.date_created = datetime.datetime.now()
            self.date_last_notified = datetime.datetime.now()
        return super(Goal, self).save(**kwargs)


class Answer(models.Model):
    goal = models.ForeignKey(Goal, related_name='answers')
    date = models.DateTimeField()
    body = models.PositiveIntegerField()

    def __unicode__(self):
        return self.body

    def save(self, **kwargs):
        if not self.pk:
            self.date = datetime.datetime.now()
        return super(Answer, self).save(**kwargs)
