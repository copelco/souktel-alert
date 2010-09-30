import django_filters
from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from rapidsms.models import Contact, Connection

from group_messaging import models as gm
from rapidsms.contrib.messagelog.tables import MessageTable
from rapidsms.contrib.messagelog.models import Message


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


class RecipientForm(forms.ModelForm):
    
    class Meta:
        model = Contact
        exclude = ('language', 'name')

    def __init__(self, *args, **kwargs):
        super(RecipientForm, self).__init__(*args, **kwargs)
        self.fields['site'].required = True
        self.fields['active'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields.keyOrder = ('first_name', 'last_name', 'comment',
                                'site', 'user', 'active')


class ConnectionInlineForm(forms.ModelForm):

    class Meta:
        model = Connection

    def __init__(self, *args, **kwargs):
        super(ConnectionInlineForm, self).__init__(*args, **kwargs)
        self.fields['backend'].required = True
        self.fields['identity'].required = True


ConnectionFormset = inlineformset_factory(Contact, Connection, extra=1,
                                          form=ConnectionInlineForm)


class logFilter(django_filters.FilterSet):

    sender = django_filters.CharFilter(name='sender',lookup_type='icontains')
    status_text = django_filters.CharFilter(name='status_text',lookup_type='icontains')
    identity = django_filters.CharFilter(name='identity',lookup_type='icontains')
    short_text = django_filters.CharFilter(name='text',lookup_type='icontains')
    
    class Meta:
        model = gm.OutgoingLog
        fields = ['sender', 'status']


class messageslogFilter(django_filters.FilterSet):

    contact = django_filters.CharFilter(name='contact',lookup_type='icontains')
    connection = django_filters.CharFilter(name='connection',lookup_type='icontains')
    direction = django_filters.CharFilter(name='direction')
    date = django_filters.CharFilter(name='date',lookup_type='icontains')
    text = django_filters.CharFilter(name='text',lookup_type='icontains')

    class Meta:
        model = Message
        fields = ['contact', 'connection', 'direction', 'date', 'text']

