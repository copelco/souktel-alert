import urllib
import urllib2
import urlparse
import pprint
import datetime
import time

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
        self.debug('configured (%s/%s)' % (self.user, self.api_id))

    def _prepare_message(self, message):
        return {
            'user': self.user,
            'password': self.password,
            'api_id': self.api_id,
            'to': message.connection.identity,
            'text': message.text,
        }

    def send(self, message):
        data = self._prepare_message(message)
        self.debug('send: %s %s' % (message, data))
        response = urllib2.urlopen(self.url, urllib.urlencode(data))
        self.debug('response: %s' % response)
