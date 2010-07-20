import unittest
import urllib
import logging

from nose.tools import assert_equals, assert_raises, assert_true

from rapidsms.tests.harness import MockRouter
from rapidsms.models import Connection, Contact, Backend
from rapidsms.messages.outgoing import OutgoingMessage

from rclickatell.backend import ClickatellBackend


logging.basicConfig(level=logging.DEBUG)
router = MockRouter()
backend = Backend.objects.create(name='Clickatell')
contact = Contact.objects.create(name='Test Contact')
connection = Connection.objects.create(contact=contact, backend=backend)


def test_outgoing_message():
    conf = {'user': 'test', 'password': 'abc', 'api_id': '1234'}
    clickatell = ClickatellBackend(name="clickatell", router=router, **conf)
    message = OutgoingMessage(connection, 'abc')
    data = clickatell._prepare_message(message)
    keys = ('user', 'password', 'api_id', 'to', 'text')
    for key in keys:
        assert_true(key in data)
    assert_equals('abc', data['text'])
