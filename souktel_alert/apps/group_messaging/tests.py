from django.test import TestCase
from django.contrib.auth.models import User

from rapidsms.models import Contact, Connection, Backend
from rapidsms.tests.harness import MockRouter

from group_messaging.app import App as MessagesApp
from group_messaging import models as gm


class TestSchedule(TestCase):
    def setUp(self):
        self.sender = Contact.objects.create(first_name='John',
                                             last_name='Doe')
        self.recipient = Contact.objects.create(first_name='John',
                                                last_name='Doe')
        self.message = gm.OutgoingLog.objects.create(sender=self.sender,
                                                     recipient=self.recipient,
                                                     text='test',
                                                     status=gm.OutgoingLog.QUEUED)
        self.router = MockRouter()
        self.app = MessagesApp(router=self.router)

    def test_messages_send_cron_job(self):
        self.app.send_messages(dry_run=True)
        msg = gm.OutgoingLog.objects.all()[0]
        self.assertEqual(msg.status, str(gm.OutgoingLog.DELIVERED))

