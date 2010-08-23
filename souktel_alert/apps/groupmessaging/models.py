#!/usr/bin/env python
# encoding=utf-8

''' Group Messaging Models '''

from django.db import models
from django.contrib.auth.models import User, UserManager
from django.utils.translation import ugettext as _, ugettext_lazy


class Site(models.Model):
    ''' Site Model

    Stores Top Level Entity
    Sites holds groups and users and recipients '''

    name = models.CharField(max_length=50, verbose_name=ugettext_lazy(u"Name"))
    active = models.BooleanField(default=True, \
                                 verbose_name=ugettext_lazy(u"Enabled?"))
    credit = models.PositiveIntegerField(default=0, \
                                         verbose_name=ugettext_lazy(u"Units"))
    manager = models.ForeignKey('WebUser', blank=True, null=True, \
                                related_name='managing', \
                                verbose_name=ugettext_lazy(u"Manager"))

    def __unicode__(self):
        return _(u"%(name)s") % {'name': self.name}


class WebUser(User):
    ''' WebUser Model

    System User which connects to web interface '''

    # Use UserManager to get the create_user method, etc.
    objects = UserManager()

    recipient = models.ForeignKey('Recipient', blank=True, null=True, \
                                  verbose_name=ugettext_lazy(u"Recipient"))
    site = models.ForeignKey('Site', related_name='managing', \
                             verbose_name=ugettext_lazy(u"Site"))

    comment = models.CharField(max_length=100, blank=True, \
                               verbose_name=ugettext_lazy(u"Comment"))


class Group(models.Model):
    ''' Group Model

    Group holds recipients and Messages '''

    class Meta:

        unique_together = ('code', 'site')

    code = models.CharField(max_length='15', \
                            verbose_name=ugettext_lazy(u"Code"))
    name = models.CharField(max_length='50', \
                            verbose_name=ugettext_lazy(u"Name"))
    site = models.ForeignKey('Site', verbose_name=ugettext_lazy(u"Site"))
    active = models.BooleanField(default=True, \
                                 verbose_name=ugettext_lazy(u"Enabled?"))
    recipients = models.ManyToManyField('Recipient', blank=True, \
                                     verbose_name=ugettext_lazy(u"Recipients"))
    managers = models.ManyToManyField('WebUser', \
                                      verbose_name=ugettext_lazy(u"Managers"))

    def __unicode__(self):
        return _(u"%(name)s") % {'name': self.name}


class Recipient(models.Model):
    ''' Recipient Model

    A person with phone number and backend '''

    class Meta:
        unique_together = ('identity', 'backend')

    first_name = models.CharField(max_length=50, \
                                  verbose_name=ugettext_lazy(u"First Name"))
    last_name = models.CharField(max_length=50, \
                                 verbose_name=ugettext_lazy(u"Last Name"))

    identity = models.CharField(max_length=30, \
                                verbose_name=ugettext_lazy(u"Phone Number"))
    backend = models.CharField(max_length=15, default='dataentry', \
                               verbose_name=ugettext_lazy(u"Backend"), \
                               help_text=ugettext_lazy(u"Leave Default."))

    active = models.BooleanField(default=True, \
                                 verbose_name=ugettext_lazy(u"Enabled?"))

    site = models.ForeignKey('Site', verbose_name=ugettext_lazy(u"Site"))

    def __unicode__(self):
        return _(u"%(full_name)s") % {'full_name': self.full_name}

    @property
    def full_name(self):
        return _(u"%(first)s %(last)s") % {'first': self.first_name.title(), \
                                        'last': self.last_name.upper()}


class Message(models.Model):
    ''' Message Model '''

    name = models.CharField(max_length=50)
    text = models.TextField()
    code = models.CharField(max_length=20, blank=True, null=True)
    site = models.ForeignKey('Site')

    @property
    def short_text(self):
        if self.text.__len__() > 50:
            return _(u"%(striptext)s...") % {'striptext': self.text}
        else:
            return _(u"%(text)s") % {'text': self.text}

    def __unicode__(self):
        return _(u"%(name)s") % {'name': self.name}


class SendingLog(models.Model):
    ''' Messages Log '''

    sender = models.ForeignKey('WebUser', \
                               verbose_name=ugettext_lazy(u"Sender"))
    groups = models.ManyToManyField('Group', \
                                    verbose_name=ugettext_lazy(u"Groups"))
    recipients = models.ManyToManyField('Recipient', \
                                     verbose_name=ugettext_lazy(u"Recipients"))
    date = models.DateTimeField(auto_now_add=True, \
                                verbose_name=ugettext_lazy(u"Date"))
    text = models.TextField(verbose_name=ugettext_lazy(u"Content"))

    @property
    def short_text(self):
        if self.text.__len__() > 50:
            return _(u"%(striptext)s...") % {'striptext': self.text}
        else:
            return _(u"%(text)s") % {'text': self.text}

    def groups_list(self):
        glist = []
        for group in self.groups.all():
            glist.append(group.name)
        return _(u", ").join(glist)

    def __unicode__(self):
        return _(u"From %(from)s to %(groups)s on %(date)s: %(text)s") % \
               {'text': self.short_text, 'groups': self.groups_list(),
                'date': self.date.strftime('%x'), 'from': self.sender}


class OutgoingLog(models.Model):
    ''' Outgoing messages Log

    Stores every single SMS sent
    Status to be updated by gateway '''

    PENDING = 0
    DELIVERED = 1
    TIMEOUT = 2
    FAILED = 3
    QUEUED = 4

    VERBOSE_PENDING = _(u"Sent")
    VERBOSE_DELIVERED = _(u"Delivered")
    VERBOSE_TIMEOUT = _(u"Timed Out")
    VERBOSE_FAILED = _(u"Failed")
    VERBOSE_QUEUED = _(u"Queued")

    STATUSES = (
        (QUEUED, ugettext_lazy(VERBOSE_QUEUED)),
        (PENDING, ugettext_lazy(VERBOSE_PENDING)),
        (DELIVERED, ugettext_lazy(VERBOSE_DELIVERED)),
        (TIMEOUT, ugettext_lazy(VERBOSE_TIMEOUT)),
        (FAILED, ugettext_lazy(VERBOSE_FAILED)),
    )

    RAW_STATUSES = [VERBOSE_PENDING, VERBOSE_DELIVERED, \
                    VERBOSE_TIMEOUT, VERBOSE_FAILED,VERBOSE_QUEUED]

    sender = models.ForeignKey('WebUser', \
                               verbose_name=ugettext_lazy(u"Sender"))
    identity = models.CharField(max_length=30, \
                                verbose_name=ugettext_lazy(u"Identity"))
    backend = models.CharField(max_length=15, \
                               verbose_name=ugettext_lazy(u"Backend"))
    text = models.TextField(verbose_name=ugettext_lazy(u"Content"))
    status = models.CharField(max_length=1, choices=STATUSES, default=QUEUED, \
                              verbose_name=ugettext_lazy(u"Status"))
    sent_on = models.DateTimeField(blank=True, null=True, \
                                   verbose_name=ugettext_lazy(u"Send Date"))
    received_on = models.DateTimeField(blank=True, null=True, \
                                 verbose_name=ugettext_lazy(u"Reception Date"))

    def text_length(self):
        return self.text.__len__()

    @property
    def short_text(self):
        if self.text.__len__() > 50:
            return _(u"%(striptext)s...") % {'striptext': self.text}
        else:
            return _(u"%(text)s") % {'text': self.text}

    @property
    def status_text(self):
        try:
            return self.RAW_STATUSES[int(self.status)]
        except:
            return self.status

    def __unicode__(self):
        return _(u"%(text)s to %(identity)s: %(status)s") % \
               {'text': self.text, 'identity': self.identity, \
                'status': self.status_text}

class Survey(models.Model):

    survey_id = models.CharField(max_length=10, primary_key=True,
            db_column = 'id')
    reference_code = models.CharField(max_length='15')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(auto_now_add=True)
    reg_required = models.CharField(max_length=10)
    addition_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)
    site = models.ForeignKey('Site')

    def __unicode__(self):
        return _(u"%(full_name)s") % {'full_name': self.full_name}

class Questions(models.Model):
    class Meta:
        unique_together = ('question_id', 'survey_id')

    question_id = models.CharField(max_length=10, primary_key=True,
            db_column = 'id')
    survey_id = models.ForeignKey('Survey')
    fst = models.CharField(max_length=1)
    qtype = models.CharField(max_length=1)
    next_sid = models.CharField(max_length=10)
    next_qid = models.CharField(max_length=10)
    def __unicode__(self):
        return _(u"%(full_name)s") % {'full_name': self.full_name}

class SurveyAnswerE(models.Model):
    class Meta:
        unique_together = ('survey_id', 'question_id')

    id = models.CharField(max_length=10, primary_key=True,
            db_column = 'id')
    survey_id = models.ForeignKey('Survey')
    question_id = models.ForeignKey('Questions')
    mobile = models.CharField(max_length=20)
    ans_text = models.CharField(max_length=160)

    def __unicode__(self):
        return _(u"%(full_name)s") % {'full_name': self.full_name}


class SurveyAnswerM(models.Model):

    id = models.CharField(max_length=10, primary_key=True, db_column = 'id')
    survey_id = models.ForeignKey('Survey')
    question_id = models.ForeignKey('Questions')
    option_id = models.ForeignKey('SurveyOption')
    mobile = models.CharField(max_length=20)

    def __unicode__(self):
        return _(u"%(full_name)s") % {'full_name': self.full_name}

class SurveyCurrent(models.Model):
    
    id = models.CharField(max_length=10, primary_key=True, db_column = 'id')
    survey_id = models.ForeignKey('Survey')
    question_id = models.ForeignKey('Questions')
    mobile = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return _(u"%(full_name)s") % {'full_name': self.full_name}

class SurveyMask(models.Model):
    
    id = models.CharField(max_length=10, primary_key=True, db_column = 'id')
    survey_id = models.ForeignKey('Survey')
    shortcode = models.CharField(max_length=20)
    mask = models.CharField(max_length=20)

    def __unicode__(self):
        return _(u"%(full_name)s") % {'full_name': self.full_name}
    
class SurveyMembers(models.Model):

    id = models.CharField(max_length=10, primary_key=True, db_column = 'id')
    survey_id = models.ForeignKey('Survey')
    mobile = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return _(u"%(full_name)s") % {'full_name': self.full_name}

class SurveyOption(models.Model):

    class Meta:
        unique_together = ('option_id','survey_id', 'question_id')

    option_id =  models.CharField(max_length=20)
    question_id = models.ForeignKey('Questions')
    survey_id = models.ForeignKey('Survey')
    next_sid = models.CharField(max_length=20)
    next_qid = models.CharField(max_length=20)

    def __unicode__(self):
        return _(u"%(full_name)s") % {'full_name': self.full_name}

class SurveyOptionTitle(models.Model):

    option_id = models.CharField(max_length=20)
    question_id = models.ForeignKey('Questions')
    survey_id = models.ForeignKey('Survey')
    title = models.CharField(max_length=160)

    def __unicode__(self):
        return _(u"%(full_name)s") % {'full_name': self.full_name}

class SurveyQuestion(models.Model):

    class Meta:
        unique_together = ('question_id','survey_id')

    question_id = models.ForeignKey('Questions')
    survey_id = models.ForeignKey('Survey')
    title = models.CharField(max_length=160)

    def __unicode__(self):
        return _(u"%(full_name)s") % {'full_name': self.full_name}

class SurveyTitle(models.Model):
    id = models.CharField(max_length=10, primary_key=True, db_column = 'id')
    survey_id = models.ForeignKey('Survey')
    title = models.CharField(max_length=160)
    description = models.TextField()

class System(models.Model):

    sys_id = models.CharField(max_length=10, primary_key=True, db_column = 'id')
    prefix = models.CharField(max_length=30, unique=True)
    reference_code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=160)
    status = models.CharField(max_length=2)
    addition_dat = models.DateTimeField(auto_now_add=True)
    api_id = models.CharField(max_length=10)
    api_key = models.CharField(max_length=10)

    def __unicode__(self):
        return _(u"%(full_name)s") % {'full_name': self.full_name}
