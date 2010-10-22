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


from decisiontree import models as dt

from decisiontree.handlers.results import ResultsHandler
from decisiontree.app import App as DecisionApp


class ResultsTest(TestCase):
    def setUp(self):
        self.backend = Backend.objects.create(name='test-backend')
        self.contact = Contact.objects.create(first_name='John',
                                              last_name='Doe')
        self.connection = Connection.objects.create(contact=self.contact,
                                                    backend=self.backend,
                                                    identity='1112223333')
        self.router = MockRouter()
        text = 'Do you like apples or squash more?'
        self.q = dt.Question.objects.create(text=text)
        self.fruit = dt.Answer.objects.create(type='A', name='apples',
                                              answer='apples')
        self.state = dt.TreeState.objects.create(name='food', question=self.q)
        self.tree = dt.Tree.objects.create(trigger='food',
                                           root_state=self.state)

    def _send(self, text):
        msg = IncomingMessage(self.connection, text)
        handler = ResultsHandler(self.router, msg)
        handler.handle(msg.text)
        return handler

    def test_survey_does_not_exist(self):
        handler = self._send('i-do-not-exist')
        response = handler.msg.responses[0].text
        self.assertEqual(response, 'Survey "i-do-not-exist" does not exist')

    def test_empty_summary(self):
        handler = self._send('food')
        response = handler.msg.responses[0].text
        self.assertEqual(response, 'No summary for "food" survey')

    def test_summary_response(self):
        self.tree.summary = '10 people like food'
        self.tree.save()
        handler = self._send('food')
        response = handler.msg.responses[0].text
        self.assertEqual(response, '10 people like food')

    def test_percent_in_summary(self):
        self.tree.summary = 'we are 100%'
        self.tree.save()
        handler = self._send('food')
        response = handler.msg.responses[0].text
        self.assertEqual(response, 'we are 100%')


class CreateDataTest(TestCase):

    def random_string(self, length=255, extra_chars=''):
        chars = string.letters + extra_chars
        return ''.join([random.choice(chars) for i in range(length)])

    def create_tree(self, data={}):
        defaults = {
            'trigger': self.random_string(5),
        }
        defaults.update(data)
        if 'root_state' not in data:
            defaults['root_state'] = self.create_state()
        return dt.Tree.objects.create(**defaults)

    def create_state(self, data={}):
        defaults = {
            'name': self.random_string(10),
        }
        defaults.update(data)
        if 'question' not in defaults:
            defaults['question'] = self.create_question()
        return dt.TreeState.objects.create(**defaults)

    def create_question(self, data={}):
        defaults = {
            'text': self.random_string(15),
        }
        defaults.update(data)
        return dt.Question.objects.create(**defaults)
    
    def create_trans(self, data={}):
        defaults = {}
        defaults.update(data)
        if 'current_state' not in defaults:
            defaults['current_state'] = self.create_state()
        if 'answer' not in defaults:
            defaults['answer'] = self.create_answer()
        if 'next_state' not in defaults:
            defaults['next_state'] = self.create_state()
        return dt.Transition.objects.create(**defaults)

    def create_answer(self, data={}):
        defaults = {
            'name': self.random_string(15),
            'type': 'A',
            'answer': self.random_string(5),
        }
        defaults.update(data)
        return dt.Answer.objects.create(**defaults)
    
    def create_tag(self, data={}):
        defaults = {
            'name': self.random_string(15),
        }
        defaults.update(data)
        return dt.Tag.objects.create(**defaults)


class BasicSurveyTest(CreateDataTest):
    def setUp(self):
        self.backend = Backend.objects.create(name='test-backend')
        self.contact = Contact.objects.create(first_name='John',
                                              last_name='Doe')
        self.connection = Connection.objects.create(contact=self.contact,
                                                    backend=self.backend,
                                                    identity='1112223333')
        self.router = MockRouter()
        self.app = DecisionApp(router=self.router)

    def _send(self, text):
        msg = IncomingMessage(self.connection, text)
        self.app.handle(msg)
        return msg

    def test_invalid_trigger(self):
        tree = self.create_tree(data={'trigger': 'food'})
        trans = self.create_trans(data={'current_state': tree.root_state})
        msg = self._send('i-do-not-exist')
        self.assertTrue(len(msg.responses) == 0)

    def test_valid_trigger(self):
        tree = self.create_tree(data={'trigger': 'food'})
        trans = self.create_trans(data={'current_state': tree.root_state})
        msg = self._send('food')
        question = trans.current_state.question.text
        self.assertTrue(question in msg.responses[0].text)

    def test_basic_response(self):
        tree = self.create_tree(data={'trigger': 'food'})
        trans = self.create_trans(data={'current_state': tree.root_state})
        self._send('food')
        answer = trans.answer.answer
        msg = self._send(answer)
        next_question = trans.next_state.question.text
        self.assertTrue(next_question in msg.responses[0].text)

    def test_error_response(self):
        tree = self.create_tree(data={'trigger': 'food'})
        trans = self.create_trans(data={'current_state': tree.root_state})
        self._send('food')
        msg = self._send('bad-answer')
        self.assertTrue('is not a valid answer' in msg.responses[0].text)

    def test_error_response_from_question(self):
        tree = self.create_tree(data={'trigger': 'food'})
        trans = self.create_trans(data={'current_state': tree.root_state})
        tree.root_state.question.error_response = 'my error response'
        tree.root_state.question.save()
        self._send('food')
        msg = self._send('bad-answer')
        self.assertTrue('my error response' == msg.responses[0].text)

    def test_sequence_start(self):
        tree = self.create_tree(data={'trigger': 'food'})
        trans = self.create_trans(data={'current_state': tree.root_state})
        self._send('food')
        answer = trans.answer.answer
        msg = self._send(answer)
        entry = trans.entries.all()[0]
        self.assertEqual(entry.sequence_id, 1)

    def test_sequence_increment(self):
        tree = self.create_tree(data={'trigger': 'food'})
        trans1 = self.create_trans(data={'current_state': tree.root_state})
        trans2 = self.create_trans(data={'current_state': trans1.next_state})
        self._send('food')
        msg = self._send(trans1.answer.answer)
        msg = self._send(trans2.answer.answer)
        entry = trans2.entries.order_by('-sequence_id')[0]
        self.assertEqual(entry.sequence_id, 2)

    def test_sequence_end(self):
        tree = self.create_tree(data={'trigger': 'food'})
        trans1 = self.create_trans(data={'current_state': tree.root_state})
        self._send('food')
        session = self.connection.session_set.all()[0]
        self.assertNotEqual(session.state, None)
        msg = self._send('end')
        session = self.connection.session_set.all()[0]
        self.assertEqual(session.state, None)
        self.assertTrue(session.canceled)
        self.assertEqual(msg.responses[0].text,
                         "Your session with 'food' has ended")


class DigestTest(CreateDataTest):
    def setUp(self):
        self.backend = Backend.objects.create(name='test-backend')
        self.contact = Contact.objects.create(first_name='John',
                                              last_name='Doe')
        self.connection = Connection.objects.create(contact=self.contact,
                                                    backend=self.backend,
                                                    identity='1112223333')
        self.router = MockRouter()
        self.app = DecisionApp(router=self.router)
        self.user = User.objects.create_user('test', 'a@a.com', 'abc')
        self.fruit_tag = dt.Tag.objects.create(name='fruit')
        self.fruit_tag.recipients.add(self.user)

    def _send(self, text):
        msg = IncomingMessage(self.connection, text)
        self.app.handle(msg)
        return msg
    
    def test_auto_tag_notification(self):
        tree = self.create_tree(data={'trigger': 'food'})
        trans1 = self.create_trans(data={'current_state': tree.root_state})
        trans1.tags.add(self.fruit_tag)
        self._send('food')
        msg = self._send(trans1.answer.answer)
        entry = trans1.entries.order_by('-sequence_id')[0]
        self.assertTrue(self.fruit_tag.pk in entry.tags.values_list('pk', flat=True))
        notification = dt.TagNotification.objects.all()[0]
        self.assertEqual(notification.entry.pk, entry.pk)

    def test_cron_job(self):
        tree = self.create_tree(data={'trigger': 'food'})
        trans1 = self.create_trans(data={'current_state': tree.root_state})
        trans2 = self.create_trans(data={'current_state': trans1.next_state})
        trans1.tags.add(self.fruit_tag)
        self._send('food')
        msg = self._send(trans1.answer.answer)
        msg = self._send(trans2.answer.answer)
        self.app.status_update()
        self.assertEquals(len(mail.outbox), 1)
        notification = dt.TagNotification.objects.all()[0]
        self.assertTrue(notification.sent)
