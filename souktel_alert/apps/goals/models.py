import datetime

from django.db import models

from rapidsms.models import Connection, Contact


class Goal(models.Model):
    REPEAT_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )
    
    contact = models.ForeignKey(Contact, related_name='goals')
    date_created = models.DateTimeField()
    date_last_notified = models.DateTimeField(null=True, blank=True)
    date_next_notified = models.DateTimeField(null=True, blank=True)
    schedule_start_date = models.DateTimeField(null=True, blank=True)
    schedule_repeat = models.CharField(max_length=16, choices=REPEAT_CHOICES,
                                       blank=True)
    body = models.TextField()
    in_session = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)

    def __unicode__(self):
        return self.body

    def save(self, **kwargs):
        if not self.pk:
            self.date_created = datetime.datetime.now()
        return super(Goal, self).save(**kwargs)


class Answer(models.Model):
    goal = models.ForeignKey(Goal, related_name='answers')
    date = models.DateTimeField()
    body = models.PositiveIntegerField()

    def __unicode__(self):
        return str(self.body)

    def save(self, **kwargs):
        if not self.pk:
            self.date = datetime.datetime.now()
        return super(Answer, self).save(**kwargs)
