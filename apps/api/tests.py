# -*- coding: utf-8 -*-

from datetime import datetime

from django.test import TestCase
from django.utils import simplejson as json
from django.conf import settings

from api.helpers import timestamp
from catalogue.models import Book, Tag


class ApiTest(TestCase):

    def setUp(self):
        self.old_api_wait = settings.API_WAIT
        settings.API_WAIT = -1

    def tearDown(self):
        settings.API_WAIT = self.old_api_wait


class ChangesTest(ApiTest):

    def test_basic(self):
        book = Book(title='A Book')
        book.save()
        tag = Tag.objects.create(category='author', name='Author')
        book.tags = [tag]
        book.save()

        changes = json.loads(self.client.get('/api/changes/0.json?book_fields=title&tag_fields=name').content)
        self.assertEqual(changes['updated']['books'], 
                         [{'id': book.id, 'title': book.title}],
                         'Invalid book format in changes')
        self.assertEqual(changes['updated']['tags'], 
                         [{'id': tag.id, 'name': tag.name}],
                         'Invalid tag format in changes')


class BookChangesTests(ApiTest):

    def setUp(self):
        super(BookChangesTests, self).setUp()
        self.book = Book.objects.create(slug='slug')

    def test_basic(self):
        # test book in book_changes.added
        changes = json.loads(self.client.get('/api/book_changes/0.json').content)
        self.assertEqual(len(changes['updated']),
                         1,
                         'Added book not in book_changes.updated')

    def test_deleted_disappears(self):
        # test deleted book disappears
        Book.objects.all().delete()
        changes = json.loads(self.client.get('/api/book_changes/0.json').content)
        self.assertEqual(len(changes), 1,
                         'Deleted book should disappear.')

    def test_shelf(self):
        changed_at = self.book.changed_at
        print changed_at

        # putting on a shelf should not update changed_at
        shelf = Tag.objects.create(category='set', slug='shelf')
        self.book.tags = [shelf]
        self.assertEqual(self.book.changed_at,
                         changed_at)

class TagChangesTests(ApiTest):

    def setUp(self):
        super(TagChangesTests, self).setUp()
        self.tag = Tag.objects.create(category='author')
        self.book = Book.objects.create()
        self.book.tags = [self.tag]
        self.book.save()

    def test_added(self):
        # test tag in tag_changes.added
        changes = json.loads(self.client.get('/api/tag_changes/0.json').content)
        self.assertEqual(len(changes['updated']),
                         1,
                         'Added tag not in tag_changes.updated')

    def test_empty_disappears(self):
        self.book.tags = []
        self.book.save()
        changes = json.loads(self.client.get('/api/tag_changes/0.json').content)
        self.assertEqual(len(changes), 1,
                         'Empty or deleted tag should disappear.')
