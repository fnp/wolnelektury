# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from os import path
import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings

from catalogue.models import Book, Tag
from picture.forms import PictureImportForm
from picture.models import Picture
import picture.tests


@override_settings(
    NO_SEARCH_INDEX=True,
    CACHES={'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}},
)
class ApiTest(TestCase):
    def load_json(self, url):
        content = self.client.get(url).content
        try:
            data = json.loads(content)
        except ValueError:
            self.fail('No JSON could be decoded: %s' % content)
        return data

    def assert_json_response(self, url, name):
        data = self.load_json(url)
        with open(path.join(path.dirname(__file__), 'res', 'responses', name)) as f:
            good_data = json.load(f)
        self.assertEqual(data, good_data, json.dumps(data, indent=4))

    def assert_slugs(self, url, slugs):
        have_slugs = [x['slug'] for x in self.load_json(url)]
        self.assertEqual(have_slugs, slugs, have_slugs)


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
        xml = SimpleUploadedFile(
            'composition8.xml', open(path.join(picture.tests.__path__[0], "files", slug + ".xml")).read())
        img = SimpleUploadedFile(
            'kompozycja-8.png', open(path.join(picture.tests.__path__[0], "files", slug + ".png")).read())

        import_form = PictureImportForm({}, {
            'picture_xml_file': xml,
            'picture_image_file': img
            })

        assert import_form.is_valid()
        if import_form.is_valid():
            import_form.save()

        Picture.objects.get(slug=slug)


class BooksTests(ApiTest):
    fixtures = ['test-books.yaml']

    def test_books(self):
	self.assert_json_response('/api/books/', 'books.json')
	self.assert_json_response('/api/books/?new_api=true', 'books.json')

        self.assert_slugs('/api/audiobooks/', ['parent'])
        self.assert_slugs('/api/daisy/', ['parent'])
        self.assert_slugs('/api/newest/', ['parent'])
        self.assert_slugs('/api/parent_books/', ['parent'])
        self.assert_slugs('/api/recommended/', ['parent'])

        # Book paging.
        self.assert_slugs('/api/books/after/grandchild/count/1/', ['parent'])
        self.assert_slugs('/api/books/?new_api=true&after=$grandchild$3&count=1', ['parent'])

        # By tag.
	self.assert_slugs('/api/authors/john-doe/books/', ['parent'])
	self.assert_slugs('/api/genres/sonet/books/?authors=john-doe', ['parent'])
        # It is probably a mistake that this doesn't filter:
	self.assert_slugs('/api/books/?authors=john-doe', ['child', 'grandchild', 'parent'])

	# Parent books by tag.
        # Notice this contains a grandchild, if a child doesn't have the tag.
        # This probably isn't really intended behavior and should be redefined.
	self.assert_slugs('/api/genres/sonet/parent_books/', ['grandchild', 'parent'])

    def test_ebooks(self):
        self.assert_json_response('/api/ebooks/', 'ebooks.json')

    def test_filter_books(self):
        self.assert_json_response('/api/filter-books/', 'filter-books.json')
        self.assert_slugs(
            '/api/filter-books/?lektura=false&preview=false',
            ['child', 'grandchild', 'parent'])
        self.assert_slugs(
            '/api/filter-books/?lektura=true',
            [])

        Book.objects.filter(slug='child').update(preview=True)
        self.assert_slugs('/api/filter-books/?preview=true', ['child'])
        self.assert_slugs('/api/filter-books/?preview=false', ['grandchild', 'parent'])

        self.assert_slugs('/api/filter-books/?audiobook=true', ['parent'])
        self.assert_slugs('/api/filter-books/?audiobook=false', ['child', 'grandchild'])

        self.assert_slugs('/api/filter-books/?genres=wiersz', ['child'])

        self.assert_slugs('/api/filter-books/?search=parent', ['parent'])

    def test_collections(self):
        self.assert_json_response('/api/collections/', 'collections.json')
        self.assert_json_response('/api/collections/a-collection/', 'collection.json')

    def test_book(self):
	self.assert_json_response('/api/books/parent/', 'books-parent.json')
	self.assert_json_response('/api/books/child/', 'books-child.json')
	self.assert_json_response('/api/books/grandchild/', 'books-grandchild.json')

    def test_tags(self):
	# List of tags by category.
	self.assert_json_response('/api/genres/', 'tags.json')

    def test_fragments(self):
        # This is not supported, though it probably should be.
	#self.assert_json_response('/api/books/child/fragments/', 'fragments.json')

	self.assert_json_response('/api/genres/wiersz/fragments/', 'fragments.json')
	self.assert_json_response('/api/genres/wiersz/fragments/', 'fragments.json')

        self.assert_json_response('/api/books/child/fragments/an-anchor/', 'fragment.json')


class BlogTests(ApiTest):
    def test_get(self):
        self.assertEqual(self.load_json('/api/blog/'), [])


class PreviewTests(ApiTest):
    def unauth(self):
        self.assert_json_response('/api/preview/', 'preview.json')


