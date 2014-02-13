# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from os import path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
import json

from catalogue.models import Book, Tag
from picture.forms import PictureImportForm
from picture.models import Picture
import picture.tests


@override_settings(
    API_WAIT=-1,
    CACHES = {'api': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'},
              'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'},
              'permanent': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}
)
class ApiTest(TestCase):
    pass


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



class BookTests(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(category='author', slug='joe')
        self.book = Book.objects.create(title='A Book', slug='a-book')
        self.book_tagged = Book.objects.create(title='Tagged Book', slug='tagged-book')
        self.book_tagged.tags = [self.tag]
        self.book_tagged.save()

    def test_book_list(self):
        books = json.loads(self.client.get('/api/books/').content)
        self.assertEqual(len(books), 2,
                         'Wrong book list.')

    def test_tagged_books(self):
        books = json.loads(self.client.get('/api/authors/joe/books/').content)

        self.assertEqual([b['title'] for b in books], [self.book_tagged.title],
                        'Wrong tagged book list.')

    def test_detail(self):
        book = json.loads(self.client.get('/api/books/a-book/').content)
        self.assertEqual(book['title'], self.book.title,
                        'Wrong book details.')


class TagTests(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(category='author', slug='joe', name='Joe')
        self.book = Book.objects.create(title='A Book', slug='a-book')
        self.book.tags = [self.tag]
        self.book.save()

    def test_tag_list(self):
        tags = json.loads(self.client.get('/api/authors/').content)
        self.assertEqual(len(tags), 1,
                        'Wrong tag list.')

    def test_tag_detail(self):
        tag = json.loads(self.client.get('/api/authors/joe/').content)
        self.assertEqual(tag['name'], self.tag.name,
                        'Wrong tag details.')


class PictureTests(ApiTest):
    def test_publish(self):
        slug = "kandinsky-composition-viii"
        xml = SimpleUploadedFile('composition8.xml', open(path.join(picture.tests.__path__[0], "files", slug + ".xml")).read())
        img = SimpleUploadedFile('kompozycja-8.png', open(path.join(picture.tests.__path__[0], "files", slug + ".png")).read())

        import_form = PictureImportForm({}, {
            'picture_xml_file': xml,
            'picture_image_file': img
            })

        assert import_form.is_valid()
        if import_form.is_valid():
            import_form.save()

        Picture.objects.get(slug=slug)
