# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from base64 import b64encode
from os import path
import hashlib
import hmac
import json
from StringIO import StringIO
from time import time
from urllib import quote, urlencode
from urlparse import parse_qs

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from mock import patch
from piston.models import Consumer, Token

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

    def assert_response(self, url, name):
        content = self.client.get(url).content.rstrip()
        filename = path.join(path.dirname(__file__), 'res', 'responses', name)
        with open(filename) as f:
            good_content = f.read().rstrip()
        self.assertEqual(content, good_content, content)
    
    def assert_json_response(self, url, name):
        data = self.load_json(url)
        filename = path.join(path.dirname(__file__), 'res', 'responses', name)
        with open(filename) as f:
            good_data = json.load(f)
        self.assertEqual(data, good_data, json.dumps(data, indent=4))

    def assert_slugs(self, url, slugs):
        have_slugs = [x['slug'] for x in self.load_json(url)]
        self.assertEqual(have_slugs, slugs, have_slugs)


class BookTests(ApiTest):

    def setUp(self):
        self.tag = Tag.objects.create(category='author', slug='joe')
        self.book = Book.objects.create(title='A Book', slug='a-book')
        self.book_tagged = Book.objects.create(
            title='Tagged Book', slug='tagged-book')
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
        self.tag = Tag.objects.create(
            category='author', slug='joe', name='Joe')
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
            'composition8.xml',
            open(path.join(
                picture.tests.__path__[0], "files", slug + ".xml"
            )).read())
        img = SimpleUploadedFile(
            'kompozycja-8.png',
            open(path.join(
                picture.tests.__path__[0], "files", slug + ".png"
            )).read())

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
        self.assert_response('/api/books/?format=xml', 'books.xml')

        self.assert_slugs('/api/audiobooks/', ['parent'])
        self.assert_slugs('/api/daisy/', ['parent'])
        self.assert_slugs('/api/newest/', ['parent'])
        self.assert_slugs('/api/parent_books/', ['parent'])
        self.assert_slugs('/api/recommended/', ['parent'])

        # Book paging.
        self.assert_slugs('/api/books/after/grandchild/count/1/', ['parent'])
        self.assert_slugs(
            '/api/books/?new_api=true&after=$grandchild$3&count=1', ['parent'])

        # By tag.
        self.assert_slugs('/api/authors/john-doe/books/', ['parent'])
        self.assert_slugs(
            '/api/genres/sonet/books/?authors=john-doe',
            ['parent'])
        # It is probably a mistake that this doesn't filter:
        self.assert_slugs(
            '/api/books/?authors=john-doe',
            ['child', 'grandchild', 'parent'])

        # Parent books by tag.
        # Notice this contains a grandchild, if a child doesn't have the tag.
        # This probably isn't really intended behavior and should be redefined.
        self.assert_slugs(
            '/api/genres/sonet/parent_books/',
            ['grandchild', 'parent'])

    def test_ebooks(self):
        self.assert_json_response('/api/ebooks/', 'ebooks.json')

    def test_filter_books(self):
        self.assert_json_response('/api/filter-books/', 'filter-books.json')
        self.assert_slugs(
            '/api/filter-books/?lektura=false',
            ['child', 'grandchild', 'parent'])
        self.assert_slugs(
            '/api/filter-books/?lektura=true',
            [])

        self.assert_slugs(
            '/api/filter-books/?preview=true',
            ['grandchild'])
        self.assert_slugs(
            '/api/filter-books/?preview=false',
            ['child', 'parent'])

        self.assert_slugs(
            '/api/filter-books/?audiobook=true',
            ['parent'])
        self.assert_slugs(
            '/api/filter-books/?audiobook=false',
            ['child', 'grandchild'])

        self.assert_slugs('/api/filter-books/?genres=wiersz', ['child'])

        self.assert_slugs('/api/filter-books/?search=parent', ['parent'])

    def test_collections(self):
        self.assert_json_response('/api/collections/', 'collections.json')
        self.assert_json_response(
            '/api/collections/a-collection/',
            'collection.json')

    def test_book(self):
        self.assert_json_response('/api/books/parent/', 'books-parent.json')
        self.assert_json_response('/api/books/child/', 'books-child.json')
        self.assert_json_response(
            '/api/books/grandchild/',
            'books-grandchild.json')

    def test_tags(self):
        # List of tags by category.
        self.assert_json_response('/api/genres/', 'tags.json')

    def test_fragments(self):
        # This is not supported, though it probably should be.
        # self.assert_json_response(
        #     '/api/books/child/fragments/',
        #     'fragments.json')

        self.assert_json_response(
            '/api/genres/wiersz/fragments/',
            'fragments.json')
        self.assert_json_response(
            '/api/books/child/fragments/an-anchor/',
            'fragment.json')


class BlogTests(ApiTest):
    def test_get(self):
        self.assertEqual(self.load_json('/api/blog/'), [])


class PreviewTests(ApiTest):
    def unauth(self):
        self.assert_json_response('/api/preview/', 'preview.json')


class OAuth1Tests(ApiTest):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create(username='test')
        cls.consumer_secret = 'len(quote(consumer secret))>=32'
        Consumer.objects.create(
            key='client',
            secret=cls.consumer_secret
        )

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()

    def test_create_token(self):
        base_query = ("oauth_consumer_key=client&oauth_nonce=123&"
                      "oauth_signature_method=HMAC-SHA1&oauth_timestamp={}&"
                      "oauth_version=1.0".format(int(time())))
        raw = '&'.join([
            'GET',
            quote('http://testserver/api/oauth/request_token/', safe=''),
            quote(base_query, safe='')
        ])
        h = hmac.new(
            quote(self.consumer_secret) + '&', raw, hashlib.sha1
        ).digest()
        h = b64encode(h).rstrip('\n')
        sign = quote(h)
        query = "{}&oauth_signature={}".format(base_query, sign)
        response = self.client.get('/api/oauth/request_token/?' + query)
        request_token = parse_qs(response.content)

        Token.objects.filter(
            key=request_token['oauth_token'][0], token_type=Token.REQUEST
        ).update(user=self.user, is_approved=True)

        base_query = ("oauth_consumer_key=client&oauth_nonce=123&"
                      "oauth_signature_method=HMAC-SHA1&oauth_timestamp={}&"
                      "oauth_token={}&oauth_version=1.0".format(
                          int(time()), request_token['oauth_token'][0]))
        raw = '&'.join([
            'GET',
            quote('http://testserver/api/oauth/access_token/', safe=''),
            quote(base_query, safe='')
        ])
        h = hmac.new(
            quote(self.consumer_secret) + '&' +
            quote(request_token['oauth_token_secret'][0], safe=''),
            raw,
            hashlib.sha1
        ).digest()
        h = b64encode(h).rstrip('\n')
        sign = quote(h)
        query = u"{}&oauth_signature={}".format(base_query, sign)
        response = self.client.get(u'/api/oauth/access_token/?' + query)
        access_token = parse_qs(response.content)

        self.assertTrue(
            Token.objects.filter(
                key=access_token['oauth_token'][0],
                token_type=Token.ACCESS,
                user=self.user
            ).exists())


class AuthorizedTests(ApiTest):
    fixtures = ['test-books.yaml']

    @classmethod
    def setUpClass(cls):
        super(AuthorizedTests, cls).setUpClass()
        cls.user = User.objects.create(username='test')
        cls.consumer = Consumer.objects.create(
            key='client', secret='12345678901234567890123456789012')
        cls.token = Token.objects.create(
            key='123456789012345678',
            secret='12345678901234567890123456789012',
            user=cls.user,
            consumer=cls.consumer,
            token_type=Token.ACCESS,
            timestamp=time())
        cls.key = cls.consumer.secret + '&' + cls.token.secret

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        cls.consumer.delete()
        super(AuthorizedTests, cls).tearDownClass()

    def signed(self, url, method='GET', params=None):
        auth_params = {
            "oauth_consumer_key": self.consumer.key,
            "oauth_nonce": "%f" % time(),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": int(time()),
            "oauth_token": self.token.key,
            "oauth_version": "1.0",
        }

        sign_params = {}
        if params:
            sign_params.update(params)
        sign_params.update(auth_params)
        raw = "&".join([
            method.upper(),
            quote('http://testserver' + url, safe=''),
            quote("&".join(
                quote(str(k)) + "=" + quote(str(v))
                for (k, v) in sorted(sign_params.items())))
        ])
        auth_params["oauth_signature"] = quote(b64encode(hmac.new(
            self.key, raw, hashlib.sha1).digest()).rstrip('\n'))
        auth = 'OAuth realm="API", ' + ', '.join(
            '{}="{}"'.format(k, v) for (k, v) in auth_params.items())

        if params:
            url = url + '?' + urlencode(params)
        return getattr(self.client, method.lower())(
                url,
                HTTP_AUTHORIZATION=auth
            )

    def signed_json(self, url, method='GET', params=None):
        return json.loads(self.signed(url, method, params).content)

    def test_books(self):
        self.assertEqual(
            [b['liked'] for b in self.signed_json('/api/books/')],
            [False, False, False]
        )
        # This one fails in the legacy implementation
        # data = self.signed_json('/api/books/child/')
        # self.assertFalse(data['parent']['liked'])
        # self.assertFalse(data['children'][0]['liked'])

        self.assertEqual(
            self.signed_json('/api/like/parent/'),
            {"likes": False}
        )
        self.signed('/api/like/parent/', 'POST')
        self.assertEqual(
            self.signed_json('/api/like/parent/'),
            {"likes": True}
        )
        # There are several endpoints where 'liked' appears.
        self.assertTrue(self.signed_json('/api/parent_books/')[0]['liked'])
        self.assertTrue(self.signed_json(
            '/api/filter-books/', params={"search": "parent"})[0]['liked'])

        # This one fails in the legacy implementation.
        #self.assertTrue(self.signed_json(
        #    '/api/books/child/')['parent']['liked'])
        # Liked books go on shelf.
        self.assertEqual(
            [x['slug'] for x in self.signed_json('/api/shelf/likes/')],
            ['parent'])

        self.signed('/api/like/parent/', 'POST', {"action": "unlike"})
        self.assertEqual(
            self.signed_json('/api/like/parent/'),
            {"likes": False}
        )
        self.assertFalse(self.signed_json('/api/parent_books/')[0]['liked'])

    def test_reading(self):
        self.assertEqual(
            self.signed_json('/api/reading/parent/'),
            {"state": "not_started"}
        )
        self.signed('/api/reading/parent/reading/', 'post')
        self.assertEqual(
            self.signed_json('/api/reading/parent/'),
            {"state": "reading"}
        )
        self.assertEqual(
            [x['slug'] for x in self.signed_json('/api/shelf/reading/')],
            ['parent'])

    def test_subscription(self):
        self.assert_slugs('/api/preview/', ['grandchild'])
        self.assertEqual(
            self.signed_json('/api/username/'),
            {"username": "test", "premium": False})
        self.assertEqual(
            self.signed('/api/epub/grandchild/').status_code,
            401)  # Not 403 because Piston.

        with patch('api.handlers.user_is_subscribed', return_value=True):
            self.assertEqual(
                self.signed_json('/api/username/'),
                {"username": "test", "premium": True})
            with patch('django.core.files.storage.Storage.open',
                       return_value=StringIO("<epub>")):
                self.assertEqual(
                    self.signed('/api/epub/grandchild/').content,
                    "<epub>")
