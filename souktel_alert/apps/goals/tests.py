import unittest
import logging

from django.test import TransactionTestCase, TestCase

from rapidsms.models import Contact, Connection, Backend
from rapidsms.tests.scripted import TestScript

from goals.models import Goal, Answer


class TestGoals(TestScript):

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
        """ Test basic goal creation and response """
        self.assertInteraction("""
          1112223333 > goal talk to 5 teachers
          1112223333 < Your goal has been recorded.
        """)

    def test_active_session(self):
        """ Test basic answer response and reply """
        goal = Goal.objects.create(contact=self.contact, body='test',
                                   in_session=True)
        self.assertInteraction("""
        1112223333 > goal 5
        1112223333 < Thank you for your response!
        """)
        goal = self.contact.goals.all()[0]
        self.assertTrue(goal.complete)

    def test_unopened_session(self):
        """ Users can only answer a goal if a session is active """
        self.assertInteraction("""
        1112223333 > goal 5
        1112223333 < You don't currently have any open goal sessions
        """)

    def test_unrecognized(self):
        """ Users must register before using the goals app """
        self.assertInteraction("""
        5555555555 > goal my new goal
        5555555555 < You must register before using the goals app
        """)

    def test_active(self):
        """ Users must register before using the goals app """
        goal = Goal.objects.create(contact=self.contact, body='test')
        self.assertInteraction("""
        1112223333 > goal active
        1112223333 < You stated that your goal was "test". Please reply with a number between 1 and 5. Thanks!
        1112223333 > goal 5
        1112223333 < Thank you for your response!
        """)
