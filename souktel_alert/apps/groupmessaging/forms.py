from django import forms
from django.utils.translation import ugettext_lazy as _

from rapidsms.models import Contact

from groupmessaging import models as gm


class GroupForm(forms.ModelForm):

    class Meta:
        model = gm.Group

    def __init__(self, site, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['code'].label = _(u"Group code")
        self.fields['name'].label = _(u"Group name")
        contacts = Contact.objects.filter(active=True, site=site)
        self.fields['recipients'].queryset = contacts
        self.fields['recipients'].label = _(u"Group recipients")
        managers = Contact.objects.filter(site=site)
        self.fields['managers'].queryset = managers
        self.fields['managers'].label = _(u"Group managers")
