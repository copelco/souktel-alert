import unittest
import logging

from django.test import TransactionTestCase, TestCase

from rapidsms.models import Contact, Connection, Backend
from rapidsms.tests.scripted import TestScript

from goals.models import Goal, Answer


class TestGoals(TestScript):
    
    apps = ('goals',)

    def setUp(self):
        super(TestGoals, self).setUp()
        backend = Backend.objects.create(name=self.backend.name)
        self.contact = Contact.objects.create(first_name='John',
                                              last_name='Doe')
        self.connection = Connection.objects.create(contact=self.contact,
                                                    backend=backend,
                                                    identity='1112223333')
        self._init_log(logging.DEBUG)

    def testGoalCreation(self):
        self.assertInteraction("""
          1112223333 > goal talk to 5 teachers
          1112223333 < Your goal has been recorded.
        """)

    def test_active(self):
        goal = Goal.objects.create(contact=self.contact, body='test',
                                   in_session=True)
        self.assertInteraction("""
        1112223333 > goal 5
        1112223333 < Thank you for your response!
        """)
