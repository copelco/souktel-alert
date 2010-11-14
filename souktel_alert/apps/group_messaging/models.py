#!/usr/bin/env python
# encoding=utf-8

''' Group Messaging Models '''

from django.db import models
from django.contrib.auth.models import User, UserManager
from django.utils.translation import ugettext as _, ugettext_lazy

from rapidsms.models import Contact, Backend


class Site(models.Model):
    ''' Site Model

    Stores Top Level Entity
    Sites holds groups and users and recipients '''

    name = models.CharField(max_length=50, verbose_name=ugettext_lazy(u"Name"))
    active = models.BooleanField(default=True, \
                                 verbose_name=ugettext_lazy(u"Enabled?"))
    credit = models.PositiveIntegerField(default=0, \
                                         verbose_name=ugettext_lazy(u"Units"))
    manager = models.ForeignKey(Contact, blank=True, null=True, \
                                related_name='managing', \
                                verbose_name=ugettext_lazy(u"Manager"))

    def __unicode__(self):
        return _(u"%(name)s") % {'name': self.name}


class Group(models.Model):
    ''' Group Model

    Group holds recipients and Messages '''

    class Meta:
        ordering = ('name',)
        unique_together = ('code', 'site')

    code = models.CharField(max_length='15', \
                            verbose_name=ugettext_lazy(u"Code"))
    name = models.CharField(max_length='50', \
                            verbose_name=ugettext_lazy(u"Name"))
    site = models.ForeignKey('Site', verbose_name=ugettext_lazy(u"Site"),
                             null=True, blank=True)
    active = models.BooleanField(default=True, \
                                 verbose_name=ugettext_lazy(u"Enabled?"))
    recipients = models.ManyToManyField(Contact, blank=True,
                                        related_name='group_recipients',
                                        verbose_name=_(u"Recipients"))
    managers = models.ManyToManyField(Contact, related_name='group_managers',
                                      verbose_name=_(u"Managers"))

    def __unicode__(self):
        return _(u"%(name)s") % {'name': self.name}


class Message(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, unique=True)
    text = models.TextField()
    
    class Meta:
        ordering = ('name',)

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

    sender = models.ForeignKey(Contact, related_name='log_senders',
                               verbose_name=ugettext_lazy(u"Sender"))
    groups = models.ManyToManyField('Group', \
                                    verbose_name=ugettext_lazy(u"Groups"))
    recipients = models.ManyToManyField(Contact, related_name='log_recipients',
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
        (str(QUEUED), ugettext_lazy(VERBOSE_QUEUED)),
        (str(PENDING), ugettext_lazy(VERBOSE_PENDING)),
        (str(DELIVERED), ugettext_lazy(VERBOSE_DELIVERED)),
        (str(TIMEOUT), ugettext_lazy(VERBOSE_TIMEOUT)),
        (str(FAILED), ugettext_lazy(VERBOSE_FAILED)),
    )

    RAW_STATUSES = [VERBOSE_PENDING, VERBOSE_DELIVERED, \
                    VERBOSE_TIMEOUT, VERBOSE_FAILED,VERBOSE_QUEUED]

    sender = models.ForeignKey(Contact, verbose_name=_(u"Sender"),
                               related_name='outgoing_sender', blank=True, null=True)
    recipient = models.ForeignKey(Contact, verbose_name=_(u"Recipient"),
                                  related_name='outoing_recipient')
    text = models.TextField(verbose_name=_(u"Content"))
    status = models.CharField(max_length=1, choices=STATUSES, default=QUEUED,
                              verbose_name=_(u"Status"))
    sent_on = models.DateTimeField(blank=True, null=True,
                                   verbose_name=_(u"Send Date"))
    received_on = models.DateTimeField(blank=True, null=True,
                                       verbose_name=_(u"Reception Date"))

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


