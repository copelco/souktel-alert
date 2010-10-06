import datetime
import unittest
import logging

from dateutil.relativedelta import relativedelta

from django.test import TransactionTestCase, TestCase
from django.contrib.auth.models import User

from rapidsms.models import Contact, Connection, Backend
from rapidsms.tests.scripted import TestScript
from rapidsms.tests.harness import MockRouter

from goals.models import Goal, Answer
from goals.app import GoalsApp


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
        self.assertFalse(goal.in_session)

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

    def test_next_non_staff(self):
        """ Non-staff cannot use the "next" command """
        goal = Goal.objects.create(contact=self.contact, body='test')
        self.assertInteraction("""
        1112223333 > goal next
        1112223333 < Your goal has been recorded.
        """)

    def test_next_staff(self):
        """ Goals can be accessed with the "next" command """
        user = User.objects.create_user('test', 'test@abc.com', 'test')
        user.is_staff = True
        user.save()
        self.contact.user = user
        self.contact.save()
        goal = Goal.objects.create(contact=self.contact, body='test')
        self.assertInteraction("""
        1112223333 > goal next
        1112223333 < In {0}., "test" was your goal. Text "goal" with a # from 0 to 5, where 5 = great progress, 0 = no progress, e.g. "goal 4"
        1112223333 > goal 5
        1112223333 < Thank you for your response!
        """.format(datetime.date.today().strftime('%b')))

    def test_close_non_staff(self):
        """ Non-staff cannot close goals """
        goal = Goal.objects.create(contact=self.contact, body='test',
                                   in_session=True)
        self.assertInteraction("""
        1112223333 > goal close
        1112223333 < Your goal has been recorded.
        """)

    def test_close_staff(self):
        """ Goals can be closed with the "close" command """
        user = User.objects.create_user('test', 'test@abc.com', 'test')
        user.is_staff = True
        user.save()
        self.contact.user = user
        self.contact.save()
        """ Goals can be closed with the "close" command """
        goal = Goal.objects.create(contact=self.contact, body='test',
                                   in_session=True)
        self.assertInteraction("""
        1112223333 > goal close
        1112223333 < Goal "test" closed
        """)
        goal = self.contact.goals.all()[0]
        self.assertFalse(goal.in_session)
        self.assertTrue(goal.complete)


class GoalLength(TestCase):
    def setUp(self):
        self.contact = Contact.objects.create(first_name='John',
                                              last_name='Doe')
        self.goal = Goal.objects.create(contact=self.contact, body='test')

    def _body(self, length=10):
        return 'n' * length

    def test_18_chars(self):
        month = self.goal.date_created.strftime('%b')
        template = GoalsApp.template % {'month': month, 'goal': self._body(18)}
        self.assertTrue(len(template) < 160,
                        'Too long (%s): %s' % (str(len(template)), template))

    def test_20_chars(self):
        month = self.goal.date_created.strftime('%b')
        template = GoalsApp.template % {'month': month, 'goal': self._body(20)}
        self.assertTrue(len(template) < 160,
                        'Too long (%s): %s' % (str(len(template)), template))


class TestSchedule(TestCase):
    def setUp(self):
        self.contact = Contact.objects.create(first_name='John',
                                              last_name='Doe')
        self.goal = Goal.objects.create(contact=self.contact, body='test')
        self.router = MockRouter()
        self.app = GoalsApp(router=self.router)

    def test_future_start_date(self):
        """ date_next_notified should equal schedule_start_date if in future """
        now = datetime.datetime.now()
        delta = relativedelta(days=+1)
        self.goal.schedule_start_date = now + delta
        self.goal.schedule_frequency = 'daily'
        self.assertEqual(self.goal.get_next_date(), now + delta)

    def test_near_past(self):
        """ date_next_notified should equal schedule_start_date if in future """
        now = datetime.datetime.now()
        delta = relativedelta(days=+1)
        self.goal.schedule_start_date = now - delta + relativedelta(hours=+1)
        self.goal.schedule_frequency = 'daily'
        self.assertEqual(self.goal.get_next_date(),
                         self.goal.schedule_start_date + delta)

    def test_one_time(self):
        """ date_next_notified should equal schedule_start_date if one time """
        now = datetime.datetime.now()
        self.goal.schedule_start_date = now
        self.goal.schedule_frequency = 'one-time'
        self.assertEqual(self.goal.get_next_date(),
                         self.goal.schedule_start_date)

    def test_goals_to_send_cron_job(self):
        """ make sure date_next_notified is updated on cron job """
        now = datetime.datetime.now()
        delta = relativedelta(days=+1, hours=+1)
        self.goal.schedule_start_date = now - delta
        self.goal.schedule_frequency = 'daily'
        self.goal.date_next_notified = now - delta
        self.goal.save()
        self.app.status_update()
        goal = Goal.objects.get(pk=self.goal.pk)
        self.assertTrue(goal.date_next_notified > self.goal.date_next_notified)

    def test_no_goals_to_send_cron_job(self):
        """ make sure only goals with date_next_notified < now are used """
        now = datetime.datetime.now()
        delta = relativedelta(hours=+5)
        self.goal.schedule_start_date = now + delta
        self.goal.schedule_frequency = 'daily'
        self.goal.date_next_notified = now + delta
        self.goal.save()
        self.app.status_update()
        goal = Goal.objects.get(pk=self.goal.pk)
        self.assertEqual(goal.date_next_notified, self.goal.date_next_notified)
