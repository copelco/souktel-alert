import logging

from django.http import HttpResponse
from django.conf import settings

from rapidsms.models import Contact, Connection
from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.router import router


logging.basicConfig(level=logging.DEBUG)


def test(request):
    if request.GET:
        contact_id = request.GET['contact_id']
        text = request.GET['message']
        contact = Contact.objects.get(pk=contact_id)
        logging.debug('Contact: {0} ({1})'.format(contact, contact.default_connection))
        message = OutgoingMessage(contact.default_connection, text)
        logging.debug('Message: {0}'.format(message))
        router.add_app('rclickatell')
        config = settings.INSTALLED_BACKENDS['clickatell']
        module = config.pop('ENGINE')
        router.add_backend('clickatell', module, config)
        logging.debug(message.send())

    return HttpResponse('OK')
