import csv

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
        exclude = ('managers', 'site')

    def __init__(self, site, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.fields['code'].label = _(u"Group code")
        self.fields['name'].label = _(u"Group name")
        contacts = Contact.objects.order_by('last_name', 'first_name')
        self.fields['recipients'].queryset = contacts
        self.fields['recipients'].label = _(u"Group recipients")


class RecipientForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(queryset=gm.Group.objects.all(),
                                            widget=forms.CheckboxSelectMultiple,
                                            required=False)
    
    class Meta:
        model = Contact
        exclude = ('language', 'name', 'site', 'active')

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance.pk:
            kwargs['initial'] = {'groups': instance.group_recipients.all()}
        super(RecipientForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = self.fields['user'].queryset.order_by('username')
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields.keyOrder = ('first_name', 'last_name', 'comment', 'groups',
                                'user')

    def save(self):
        instance = super(RecipientForm, self).save()
        instance.group_recipients = self.cleaned_data['groups']
        return instance


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

    contact = django_filters.CharFilter(name='contact')
    connection = django_filters.CharFilter(name='connection')
    direction = django_filters.CharFilter(name='direction')
    date = django_filters.CharFilter(name='date')
    text = django_filters.CharFilter(name='text')

    class Meta:
        model = Message
        fields = ['contact', 'connection', 'direction', 'date', 'text']


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSV File')
    group = forms.ModelChoiceField(queryset=gm.Group.objects.all(),
                                   required=False)

    def save(self):
        fh = self.cleaned_data['csv_file']
        try:
            dialect = csv.Sniffer().sniff(fh.read(1024))
        except csv.Error:
            dialect = csv.excel
        fh.seek(0)
        return csv.reader(fh)


class UserForm(forms.ModelForm):

    password1 = forms.CharField(label=_("Password"), required=False,
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password (again)"), required=False,
                                widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        if not self.instance.pk:
            self.fields['password1'].required = True
            self.fields['password2'].required = True

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            msg = _("The two password fields didn't match.")
            raise forms.ValidationError(msg)
        return password2
    
    def save(self):
        user = super(UserForm, self).save(commit=False)
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]
        if password1 and password2:
            user.set_password(password1)
        user.save()
        return user
