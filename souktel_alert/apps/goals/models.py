import datetime

from dateutil.relativedelta import relativedelta

from django.db import models

from rapidsms.models import Connection, Contact


class ActiveGoalManager(models.Manager):
    def get_query_set(self):
            qs = super(ActiveGoalManager, self).get_query_set()
            return qs.filter(complete=False)


class Goal(models.Model):
    REPEAT_CHOICES = (
        ('one-time', 'One Time'),
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
    schedule_frequency = models.CharField(max_length=16, blank=True,
                                          choices=REPEAT_CHOICES)
    body = models.TextField()
    in_session = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)

    objects = models.Manager()
    active = ActiveGoalManager()

    def __unicode__(self):
        return self.body

    def get_next_date(self):
        if self.schedule_start_date and self.schedule_frequency:
            next_date = self.schedule_start_date
            frequency_map = {
                'daily': relativedelta(days=+1),
                'weekly': relativedelta(weeks=+1),
                'monthly': relativedelta(months=+1),
                'yearly': relativedelta(years=+1),
            }
            if self.schedule_frequency in frequency_map:
                now = datetime.datetime.now()
                delta = frequency_map[self.schedule_frequency]
                while next_date < now:
                    next_date += delta
            return next_date

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
