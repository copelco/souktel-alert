import urllib
import urlparse
import pprint
import datetime

from django.http import QueryDict
from django.db import DatabaseError

from rapidsms.log.mixin import LoggerMixin
from rapidsms.backends.base import BackendBase


class ClickatellBackend(BackendBase):
    '''A RapidSMS backend for Clickatell'''

    url = 'https://api.clickatell.com/http/sendmsg'

    def configure(self, user, password, api_id):
        self.user = user
        self.password = password
        self.api_id = api_id
        self.debug('configured ({0}/{1})'.format(self.user, self.api_id))

    def _prepare_message(self, message):
        return {
            'user': self.user,
            'password': self.password,
            'api_id': self.api_id,
            'to': message.contact,
            'text': message.text,
        }

    def send(self, message):
        self.debug('send: {0}'.format(message))
        data = self._prepare_message(message)
        response = urllib2.urlopen(self.url, data)
        self.debug('response: {0}'.format(response))
