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
        self.debug('Request: %s' % pprint.pformat(dict(request.GET)))
        message = self.message(request.GET)
        if message:
            self.route(message)
        return HttpResponse('OK')

    def message(self, data):
        sender = data.get('from', '')
        sms = data.get('text', '')
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
