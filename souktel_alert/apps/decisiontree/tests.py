import logging

from django.test import TransactionTestCase, TestCase
from django.contrib.auth.models import User

from rapidsms.models import Connection, Contact, Backend

from rapidsms.tests.harness import MockRouter, MockBackend
from rapidsms.models import Connection, Contact, Backend
from rapidsms.messages.outgoing import OutgoingMessage

from decisiontree import models as dt

from taggit.models import Tag


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
        self.fruit_tag = Tag.objects.create(name='fruit', slug='fruit')
        self.vegetable_tag = Tag.objects.create(name='vegetable',
                                                slug='vegetable')

    def test_proper_tagging(self):
        tagger = dt.Tagger.objects.create(answer=self.fruit)
        tagger.tags.add(self.fruit_tag)
        tags = dt.Tagger.get_tags_for_answer(self.fruit)
        self.assertTrue(self.fruit_tag in tags)
        self.assertFalse(self.vegetable_tag in tags)

    def test_entry_tagging_on_save(self):
        tagger = dt.Tagger.objects.create(answer=self.fruit)
        tagger.tags.add(self.fruit_tag)
        entry = dt.Entry.objects.create(session=self.session, sequence_id=1,
                                        transition=self.trans1, text='apples')
        self.assertTrue(self.fruit_tag in entry.tags.all(),
                        '%s not in %s' % (self.fruit_tag, entry.tags.all()))
