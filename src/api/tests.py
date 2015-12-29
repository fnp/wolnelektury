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
    NO_SEARCH_INDEX=True,
    CACHES={'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}},
    SSIFY_CACHE_ALIASES=['default'],
    SSIFY_RENDER=True,
)
class ApiTest(TestCase):
    def load_json(self, url):
        content = self.client.get(url).content
        try:
            data = json.loads(content)
        except ValueError:
            self.fail('No JSON could be decoded:', content)
        return data


class BookTests(ApiTest):

    def setUp(self):
        self.tag = Tag.objects.create(category='author', slug='joe')
        self.book = Book.objects.create(title='A Book', slug='a-book')
        self.book_tagged = Book.objects.create(title='Tagged Book', slug='tagged-book')
        self.book_tagged.tags = [self.tag]
        self.book_tagged.save()

    def test_book_list(self):
        books = self.load_json('/api/books/')
        self.assertEqual(len(books), 2,
                         'Wrong book list.')

    def test_tagged_books(self):
        books = self.load_json('/api/authors/joe/books/')

        self.assertEqual([b['title'] for b in books], [self.book_tagged.title],
                        'Wrong tagged book list.')

    def test_detail(self):
        book = self.load_json('/api/books/a-book/')
        self.assertEqual(book['title'], self.book.title,
                        'Wrong book details.')


class TagTests(ApiTest):

    def setUp(self):
        self.tag = Tag.objects.create(category='author', slug='joe', name='Joe')
        self.book = Book.objects.create(title='A Book', slug='a-book')
        self.book.tags = [self.tag]
        self.book.save()

    def test_tag_list(self):
        tags = self.load_json('/api/authors/')
        self.assertEqual(len(tags), 1,
                        'Wrong tag list.')

    def test_tag_detail(self):
        tag = self.load_json('/api/authors/joe/')
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
