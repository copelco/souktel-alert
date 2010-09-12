from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User


class ContactExtra(models.Model):

    user = models.ForeignKey(User, unique=True, null=True, blank=True)
    site = models.ForeignKey('groupmessaging.Site', null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    comment = models.CharField(max_length=100, blank=True,
                               verbose_name=_(u"Comment"))
    active = models.BooleanField(default=True, verbose_name=_(u"Enabled?"))

    def save(self, **kwargs):
        self.name = "%s %s" % (self.first_name, self.last_name)
        super(ContactExtra, self).save(**kwargs)

    class Meta:
        abstract = True
