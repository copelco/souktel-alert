import pprint
import datetime

from django.db import DatabaseError
from django.http import HttpResponse

from rjavna.http import RapidHttpBacked


class JavnaBackend(RapidHttpBacked):
    """ A RapidSMS backend for the Javna SMS API """

    def configure(self, config=None, **kwargs):
        self.config = config
        super(JavnaBackend, self).configure(**kwargs)

    def handle_request(self, request):
        self.debug('Request: %s' % pprint.pformat(dict(request.POST)))
        message = self.message(request.POST)
        if message:
            self.route(message)
        return HttpResponse('OK')

    def message(self, data):
        sms = data.get('from', '')
        sender = data.get('text', '')
        if not sms or not sender:
            self.error('Missing from or text: %s' % pprint.pformat(dict(data)))
            return None
        now = datetime.datetime.utcnow()
        try:
            msg = super(JavnaBackend, self).message(sender, sms, now)
        except DatabaseError, e:
            self.exception(e)
            raise
        return msg
