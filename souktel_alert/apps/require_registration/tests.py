import logging
import string
import random

from django.test import TransactionTestCase, TestCase
from django.contrib.auth.models import User
from django.core import mail

from rapidsms.models import Connection, Contact, Backend

from rapidsms.tests.harness import MockRouter, MockBackend
from rapidsms.models import Connection, Contact, Backend
from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.messages.incoming import IncomingMessage

from require_registration.app import RegApp


class DigestTest(TestCase):
    def setUp(self):
        self.backend = Backend.objects.create(name='test-backend')
        self.router = MockRouter()
        self.app = RegApp(router=self.router)

    def test_unregistered(self):
        connection = Connection.objects.create(backend=self.backend,
                                               identity='1112223333')
        msg = IncomingMessage(connection, 'foo')
        handled = self.app.handle(msg)
        self.assertTrue(handled)
        self.assertEqual(msg.responses[0].text,
                         'You must register first. Please reply with "reg <name>"')

    def test_registered(self):
        contact = Contact.objects.create(first_name='John', last_name='Doe')
        connection = Connection.objects.create(backend=self.backend,
                                               identity='1112223333',
                                               contact=contact)
        msg = IncomingMessage(connection, 'foo')
        handled = self.app.handle(msg)
        self.assertFalse(handled)

    def test_register(self):
        connection = Connection.objects.create(backend=self.backend,
                                               identity='1112223333')
        msg = IncomingMessage(connection, 'reg colin')
        handled = self.app.handle(msg)
        self.assertTrue(handled)
        self.assertEqual(msg.responses[0].text, 'Thank you for registering')
        conn = Connection.objects.all()[0]
        self.assertEqual(conn.contact_id, msg.connection.contact_id)
