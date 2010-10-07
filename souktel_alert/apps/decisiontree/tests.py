import logging
import string
import random

from django.test import TransactionTestCase, TestCase
from django.contrib.auth.models import User

from rapidsms.models import Connection, Contact, Backend

from rapidsms.tests.harness import MockRouter, MockBackend
from rapidsms.models import Connection, Contact, Backend
from rapidsms.messages.outgoing import OutgoingMessage
from rapidsms.messages.incoming import IncomingMessage


from decisiontree import models as dt

from decisiontree.handlers.results import ResultsHandler
from decisiontree.app import App as DecisionApp


class TaggingTest(TestCase):
    def setUp(self):
        self.backend = Backend.objects.create(name='test-backend')
        self.contact = Contact.objects.create(first_name='John',
                                              last_name='Doe')
        self.connection = Connection.objects.create(contact=self.contact,
                                                    backend=self.backend,
                                                    identity='1112223333')
        text = 'Do you like apples or squash more?'
        self.q1 = dt.Question.objects.create(text=text)
        self.fruit = dt.Answer.objects.create(type='A', name='apples',
                                              answer='apples')
        self.state1 = dt.TreeState.objects.create(name='food',
                                                  question=self.q1)
        self.tree1 = dt.Tree.objects.create(trigger='food',
                                            root_state=self.state1)
        self.trans1 = dt.Transition.objects.create(current_state=self.state1,
                                                   answer=self.fruit)
        self.session = dt.Session.objects.create(connection=self.connection,
                                                 tree=self.tree1,
                                                 state=self.state1,
                                                 num_tries=1)
        self.fruit_tag = dt.Tag.objects.create(name='fruit')
        self.vegetable_tag = dt.Tag.objects.create(name='vegetable')

    def test_entry_tagging_on_save(self):
        self.trans1.tags = [self.fruit_tag]
        self.trans1.save()
        entry = dt.Entry.objects.create(session=self.session, sequence_id=1,
                                        transition=self.trans1, text='apples')
        self.assertTrue(self.fruit_tag in entry.tags.all(),
                        '%s not in %s' % (self.fruit_tag, entry.tags.all()))


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
