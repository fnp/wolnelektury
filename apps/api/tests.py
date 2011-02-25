# -*- coding: utf-8 -*-

from datetime import datetime

from django.test import TestCase
from django.utils import simplejson as json

from api.helpers import timestamp
from catalogue.models import Book, Tag


class ChangesTests(TestCase):

    def test_basic(self):
        book = Book.objects.create(slug='a-book', title='A Book')
        tag = Tag.objects.create(category='author', slug='author', name='Author')

        print self.client.get('/api/changes/0.json?book_fields=slug&tag_fields=slug').content
        changes = json.loads(self.client.get('/api/changes/0.json?book_fields=slug&tag_fields=slug').content)
        self.assertEqual(changes['added']['books'], 
                         [{'id': book.id, 'slug': book.slug}],
                         'Invalid book format in changes')
        self.assertEqual(changes['added']['tags'], 
                         [{'id': tag.id, 'slug': tag.slug}],
                         'Invalid tag format in changes')


class BookChangesTests(TestCase):

    def setUp(self):
        self.book = Book.objects.create()

    def test_basic(self):
        # test book in book_changes.added
        changes = json.loads(self.client.get('/api/book_changes/0.json').content)
        self.assertEqual(len(changes['added']),
                         1,
                         'Added book not in book_changes.added')

        # test changed book in changed
        self.book.slug = 'a-book'
        self.book.save()
        changes = json.loads(self.client.get('/api/book_changes/%f.json' % timestamp(self.book.created_at)).content)
        self.assertEqual(changes['added'],
                         [],
                         'Changed book in book_changes.added instead of book_changes.changed.')
        self.assertEqual(len(changes['changed']),
                         1,
                         'Changed book not in book_changes.changed.')

        # test deleted book in deleted
        Book.objects.all().delete()
        changes = json.loads(self.client.get('/api/book_changes/%f.json' % timestamp(self.book.changed_at)).content)
        self.assertEqual(changes['added'],
                         [],
                         'Deleted book still in book_changes.added.')
        self.assertEqual(changes['changed'],
                         [],
                         'Deleted book still in book_changes.changed.')
        self.assertEqual(len(changes['deleted']),
                         1,
                         'Deleted book not in book_changes.deleted.')

    def test_shelf(self):
        changed_at = self.book.changed_at
        print changed_at

        # putting on a shelf should not update changed_at
        shelf = Tag.objects.create(category='set', slug='shelf')
        self.book.tags = [shelf]
        self.assertEqual(self.book.changed_at,
                         changed_at)

class TagChangesTests(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create()

    def test_basic(self):
        # test tag in tag_changes.added
        changes = json.loads(self.client.get('/api/tag_changes/0.json').content)
        self.assertEqual(len(changes['added']),
                         1,
                         'Added tag not in tag_changes.added')

        # test changed tag in changed
        self.tag.slug = 'a-tag'
        self.tag.save()
        changes = json.loads(self.client.get('/api/tag_changes/%f.json' % timestamp(self.tag.created_at)).content)
        self.assertEqual(changes['added'],
                         [],
                         'Changed tag in tag_changes.added instead of tag_changes.changed.')
        self.assertEqual(len(changes['changed']),
                         1,
                         'Changed tag not in tag_changes.changed.')

        # test deleted book in deleted
        Tag.objects.all().delete()
        changes = json.loads(self.client.get('/api/tag_changes/%f.json' % timestamp(self.tag.changed_at)).content)
        self.assertEqual(changes['added'],
                         [],
                         'Deleted tag still in tag_changes.added.')
        self.assertEqual(changes['changed'],
                         [],
                         'Deleted tag still in tag_changes.changed.')
        self.assertEqual(len(changes['deleted']),
                         1,
                         'Deleted tag not in tag_changes.deleted.')
