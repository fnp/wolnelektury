# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http.response import HttpResponse
from django.utils.functional import lazy
from django.db import models
from migdal.models import Entry
from piston.handler import AnonymousBaseHandler, BaseHandler
from piston.utils import rc
from sorl.thumbnail import default

from api.models import BookUserData
from catalogue.forms import BookImportForm
from catalogue.models import Book, Tag, BookMedia, Fragment, Collection
from catalogue.models.tag import prefetch_relations
from librarian.cover import WLCover
from paypal.rest import user_is_subscribed
from picture.models import Picture
from picture.forms import PictureImportForm
from social.utils import likes

from stats.utils import piwik_track
from wolnelektury.utils import re_escape

from . import emitters  # Register our emitters

API_BASE = WL_BASE = MEDIA_BASE = lazy(
    lambda: u'https://' + Site.objects.get_current().domain, unicode)()

SORT_KEY_SEP = '$'

category_singular = {
    'authors': 'author',
    'kinds': 'kind',
    'genres': 'genre',
    'epochs': 'epoch',
    'themes': 'theme',
    'books': 'book',
}
category_plural = {}
for k, v in category_singular.items():
    category_plural[v] = k

book_tag_categories = ['author', 'epoch', 'kind', 'genre']

book_list_fields = book_tag_categories + [
    'href', 'title', 'url', 'cover', 'cover_thumb', 'slug', 'simple_thumb', 'has_audio', 'cover_color', 'full_sort_key']


def read_tags(tags, request, allowed):
    """ Reads a path of filtering tags.

    :param str tags: a path of category and slug pairs, like: authors/an-author/...
    :returns: list of Tag objects
    :raises: ValueError when tags can't be found
    """

    def process(category, slug):
        if category == 'book':
            # FIXME: Unused?
            try:
                books.append(Book.objects.get(slug=slug))
            except Book.DoesNotExist:
                raise ValueError('Unknown book.')
        try:
            real_tags.append(Tag.objects.get(category=category, slug=slug))
        except Tag.DoesNotExist:
            raise ValueError('Tag not found')

    if not tags:
        return [], []

    tags = tags.strip('/').split('/')
    real_tags = []
    books = []
    while tags:
        category = tags.pop(0)
        slug = tags.pop(0)

        try:
            category = category_singular[category]
        except KeyError:
            raise ValueError('Unknown category.')

        if category not in allowed:
            raise ValueError('Category not allowed.')
        process(category, slug)

    for key in request.GET:
        if key in category_singular:
            category = category_singular[key]
            if category in allowed:
                for slug in request.GET.getlist(key):
                    process(category, slug)
    return real_tags, books


# RESTful handlers


class BookMediaHandler(BaseHandler):
    """ Responsible for representing media in Books. """

    model = BookMedia
    fields = ['name', 'type', 'url', 'artist', 'director']

    @classmethod
    def url(cls, media):
        """ Link to media on site. """

        return MEDIA_BASE + media.file.url

    @classmethod
    def artist(cls, media):
        return media.extra_info.get('artist_name', '')

    @classmethod
    def director(cls, media):
        return media.extra_info.get('director_name', '')


class BookDetails(object):
    """Custom fields used for representing Books."""

    @classmethod
    def href(cls, book):
        """ Returns an URI for a Book in the API. """
        return API_BASE + reverse("api_book", args=[book.slug])

    @classmethod
    def url(cls, book):
        """ Returns Book's URL on the site. """
        return WL_BASE + book.get_absolute_url()

    @classmethod
    def children(cls, book):
        """ Returns all children for a book. """
        return book.children.order_by('parent_number', 'sort_key')

    @classmethod
    def media(cls, book):
        """ Returns all media for a book. """
        return book.media.all()

    @classmethod
    def cover(cls, book):
        return MEDIA_BASE + book.cover.url if book.cover else ''

    @classmethod
    def cover_thumb(cls, book):
        return MEDIA_BASE + default.backend.get_thumbnail(
                    book.cover, "139x193").url if book.cover else ''

    @classmethod
    def simple_thumb(cls, book):
        return MEDIA_BASE + book.cover_api_thumb.url if book.cover_api_thumb else ''

    @classmethod
    def simple_cover(cls, book):
        return MEDIA_BASE + book.simple_cover.url if book.simple_cover else ''

    @classmethod
    def cover_color(cls, book):
        return WLCover.epoch_colors.get(book.extra_info.get('epoch'), '#000000')

    @classmethod
    def full_sort_key(cls, book):
        return '%s%s%s%s%s' % (book.sort_key_author, SORT_KEY_SEP, book.sort_key, SORT_KEY_SEP, book.id)

    @staticmethod
    def books_after(books, after, new_api):
        if not new_api:
            return books.filter(slug__gt=after)
        try:
            author, title, book_id = after.split(SORT_KEY_SEP)
        except ValueError:
            return Book.objects.none()
        return books.filter(Q(sort_key_author__gt=author)
                            | (Q(sort_key_author=author) & Q(sort_key__gt=title))
                            | (Q(sort_key_author=author) & Q(sort_key=title) & Q(id__gt=int(book_id))))

    @staticmethod
    def order_books(books, new_api):
        if new_api:
            return books.order_by('sort_key_author', 'sort_key', 'id')
        else:
            return books.order_by('slug')


class BookDetailHandler(BaseHandler, BookDetails):
    """ Main handler for Book objects.

    Responsible for single Book details.
    """
    allowed_methods = ['GET']
    fields = ['title', 'parent', 'children'] + Book.formats + [
        'media', 'url', 'cover', 'cover_thumb', 'simple_thumb', 'simple_cover', 'fragment_data', 'audio_length',
        'preview', 'cover_color'] + [
            category_plural[c] for c in book_tag_categories]

    @piwik_track
    def read(self, request, book):
        """ Returns details of a book, identified by a slug and lang. """
        try:
            return Book.objects.get(slug=book)
        except Book.DoesNotExist:
            return rc.NOT_FOUND


class AnonymousBooksHandler(AnonymousBaseHandler, BookDetails):
    """ Main handler for Book objects.

    Responsible for lists of Book objects.
    """
    allowed_methods = ('GET',)
    model = Book
    fields = book_list_fields

    # FIXME: Unused?
    @classmethod
    def genres(cls, book):
        """ Returns all media for a book. """
        return book.tags.filter(category='genre')

    @piwik_track
    def read(self, request, tags=None, top_level=False, audiobooks=False, daisy=False, pk=None,
             recommended=False, newest=False, books=None,
             after=None, count=None):
        """ Lists all books with given tags.

        :param tags: filtering tags; should be a path of categories
             and slugs, i.e.: authors/an-author/epoch/an-epoch/
        :param top_level: if True and a book is included in the results,
             it's children are aren't. By default all books matching the tags
             are returned.
        """
        if pk is not None:
            # FIXME: Unused?
            try:
                return Book.objects.get(pk=pk)
            except Book.DoesNotExist:
                return rc.NOT_FOUND

        try:
            tags, _ancestors = read_tags(tags, request, allowed=book_tag_categories)
        except ValueError:
            return rc.NOT_FOUND

        new_api = request.GET.get('new_api')
        if 'after' in request.GET:
            after = request.GET['after']
        if 'count' in request.GET:
            count = request.GET['count']

        if tags:
            if top_level:
                books = Book.tagged_top_level(tags)
                return books if books else rc.NOT_FOUND
            else:
                books = Book.tagged.with_all(tags)
        else:
            books = books if books is not None else Book.objects.all()
        books = self.order_books(books, new_api)

        if top_level:
            books = books.filter(parent=None)
        if audiobooks:
            books = books.filter(media__type='mp3').distinct()
        if daisy:
            books = books.filter(media__type='daisy').distinct()
        if recommended:
            books = books.filter(recommended=True)
        if newest:
            books = books.order_by('-created_at')

        if after:
            books = self.books_after(books, after, new_api)

        if new_api:
            books = books.only('slug', 'title', 'cover', 'cover_thumb', 'sort_key', 'sort_key_author')
        else:
            books = books.only('slug', 'title', 'cover', 'cover_thumb')
        for category in book_tag_categories:
            books = prefetch_relations(books, category)

        if count:
            books = books[:count]

        return books

    def create(self, request, *args, **kwargs):
        return rc.FORBIDDEN


class BooksHandler(BookDetailHandler):
    allowed_methods = ('GET', 'POST')
    model = Book
    fields = book_list_fields + ['liked']
    anonymous = AnonymousBooksHandler

    # hack, because piston is stupid
    @classmethod
    def liked(cls, book):
        return getattr(book, 'liked', None)

    def read(self, request, **kwargs):
        books = AnonymousBooksHandler().read(request, **kwargs)
        likes = set(Book.tagged.with_any(request.user.tag_set.all()).values_list('id', flat=True))

        new_books = [
            BookProxy(book).set('liked', book.id in likes)
            for book in books]
        return QuerySetProxy(new_books)

    def create(self, request, *args, **kwargs):
        if not request.user.has_perm('catalogue.add_book'):
            return rc.FORBIDDEN

        data = json.loads(request.POST.get('data'))
        form = BookImportForm(data)
        if form.is_valid():
            form.save()
            return rc.CREATED
        else:
            return rc.NOT_FOUND


class EpubHandler(BookDetailHandler):
    def read(self, request, slug):
        if not user_is_subscribed(request.user):
            return rc.FORBIDDEN
        try:
            book = Book.objects.get(slug=slug)
        except Book.DoesNotExist:
            return rc.NOT_FOUND
        response = HttpResponse(book.get_media('epub'))
        return response


class EBooksHandler(AnonymousBooksHandler):
    fields = ('author', 'href', 'title', 'cover') + tuple(Book.ebook_formats) + ('slug',)


class BookProxy(models.Model):
    class Meta:
        managed = False

    def __init__(self, book, key=None):
        self.book = book
        self.key = key

    def set(self, attr, value):
        self.__setattr__(attr, value)
        return self

    def __getattr__(self, item):
        return self.book.__getattribute__(item)


class QuerySetProxy(models.QuerySet):
    def __init__(self, l):
        self.list = l

    def __iter__(self):
        return iter(self.list)


class AnonFilterBooksHandler(AnonymousBooksHandler):
    fields = book_list_fields + ['key']

    def parse_bool(self, s):
        if s in ('true', 'false'):
            return s == 'true'
        else:
            return None

    def read(self, request):
        key_sep = '$'
        search_string = request.GET.get('search')
        is_lektura = self.parse_bool(request.GET.get('lektura'))
        is_audiobook = self.parse_bool(request.GET.get('audiobook'))
        preview = self.parse_bool(request.GET.get('preview'))

        new_api = request.GET.get('new_api')
        after = request.GET.get('after')
        count = int(request.GET.get('count', 50))
        books = self.order_books(Book.objects.distinct(), new_api)
        if is_lektura is not None:
            books = books.filter(has_audience=is_lektura)
        if is_audiobook is not None:
            if is_audiobook:
                books = books.filter(media__type='mp3')
            else:
                books = books.exclude(media__type='mp3')
        if preview is not None:
            books = books.filter(preview=preview)
        for key in request.GET:
            if key in category_singular:
                category = category_singular[key]
                if category in book_tag_categories:
                    slugs = request.GET[key].split(',')
                    tags = Tag.objects.filter(category=category, slug__in=slugs)
                    books = Book.tagged.with_any(tags, books)
        if (search_string is not None) and len(search_string) < 3:
            search_string = None
        if search_string:
            search_string = re_escape(search_string)
            books_author = books.filter(cached_author__iregex='\m' + search_string)
            books_title = books.filter(title__iregex='\m' + search_string)
            books_title = books_title.exclude(id__in=list(books_author.values_list('id', flat=True)))
            if after and (key_sep in after):
                which, key = after.split(key_sep, 1)
                if which == 'title':
                    book_lists = [(self.books_after(books_title, key, new_api), 'title')]
                else:  # which == 'author'
                    book_lists = [(self.books_after(books_author, key, new_api), 'author'), (books_title, 'title')]
            else:
                book_lists = [(books_author, 'author'), (books_title, 'title')]
        else:
            if after and key_sep in after:
                which, key = after.split(key_sep, 1)
                books = self.books_after(books, key, new_api)
            book_lists = [(books, 'book')]

        filtered_books = []
        for book_list, label in book_lists:
            book_list = book_list.only('slug', 'title', 'cover', 'cover_thumb', 'sort_key_author', 'sort_key')
            for category in book_tag_categories:
                book_list = prefetch_relations(book_list, category)
            remaining_count = count - len(filtered_books)
            new_books = [
                BookProxy(book, '%s%s%s' % (
                    label, key_sep, book.slug if not new_api else self.full_sort_key(book)))
                for book in book_list[:remaining_count]]
            filtered_books += new_books
            if len(filtered_books) == count:
                break

        return QuerySetProxy(filtered_books)


class FilterBooksHandler(BooksHandler):
    anonymous = AnonFilterBooksHandler
    fields = book_list_fields + ['key', 'liked']

    # hack, because piston is stupid
    @classmethod
    def liked(cls, book):
        return getattr(book, 'liked', None)

    def read(self, request):
        qsp = AnonFilterBooksHandler().read(request)
        likes = set(Book.tagged.with_any(request.user.tag_set.all()).values_list('id', flat=True))
        for book in qsp.list:
            book.set('liked', book.id in likes)
        return qsp


class BookPreviewHandler(BookDetailHandler):
    fields = BookDetailHandler.fields + ['slug']

    def read(self, request):
        return Book.objects.filter(preview=True)


# add categorized tags fields for Book
def _tags_getter(category):
    @classmethod
    def get_tags(cls, book):
        return book.tags.filter(category=category)
    return get_tags


def _tag_getter(category):
    @classmethod
    def get_tag(cls, book):
        return book.tag_unicode(category)
    return get_tag


def add_tag_getters():
    for plural, singular in category_singular.items():
        setattr(BookDetails, plural, _tags_getter(singular))
        setattr(BookDetails, singular, _tag_getter(singular))


add_tag_getters()


# add fields for files in Book
def _file_getter(book_format):

    @staticmethod
    def get_file(book):
        f_url = book.media_url(book_format)
        if f_url:
            return MEDIA_BASE + f_url
        else:
            return ''
    return get_file


def add_file_getters():
    for book_format in Book.formats:
        setattr(BookDetails, book_format, _file_getter(book_format))


add_file_getters()


class CollectionDetails(object):
    """Custom Collection fields."""

    @classmethod
    def href(cls, collection):
        """ Returns URI in the API for the collection. """

        return API_BASE + reverse("api_collection", args=[collection.slug])

    @classmethod
    def url(cls, collection):
        """ Returns URL on the site. """

        return WL_BASE + collection.get_absolute_url()

    @classmethod
    def books(cls, collection):
        return Book.objects.filter(collection.get_query())


class CollectionDetailHandler(BaseHandler, CollectionDetails):
    allowed_methods = ('GET',)
    fields = ['url', 'title', 'description', 'books']

    @piwik_track
    def read(self, request, slug):
        """ Returns details of a collection, identified by slug. """
        try:
            return Collection.objects.get(slug=slug)
        except Collection.DoesNotExist:
            return rc.NOT_FOUND


class CollectionsHandler(BaseHandler, CollectionDetails):
    allowed_methods = ('GET',)
    model = Collection
    fields = ['url', 'href', 'title']

    @piwik_track
    def read(self, request):
        """ Returns all collections. """
        return Collection.objects.all()


class TagDetails(object):
    """Custom Tag fields."""

    @classmethod
    def href(cls, tag):
        """ Returns URI in the API for the tag. """

        return API_BASE + reverse("api_tag", args=[category_plural[tag.category], tag.slug])

    @classmethod
    def url(cls, tag):
        """ Returns URL on the site. """

        return WL_BASE + tag.get_absolute_url()


class TagDetailHandler(BaseHandler, TagDetails):
    """ Responsible for details of a single Tag object. """

    fields = ['name', 'url', 'sort_key', 'description']

    @piwik_track
    def read(self, request, category, slug):
        """ Returns details of a tag, identified by category and slug. """

        try:
            category_sng = category_singular[category]
        except KeyError:
            return rc.NOT_FOUND

        try:
            return Tag.objects.get(category=category_sng, slug=slug)
        except Tag.DoesNotExist:
            return rc.NOT_FOUND


class TagsHandler(BaseHandler, TagDetails):
    """ Main handler for Tag objects.

    Responsible for lists of Tag objects
    and fields used for representing Tags.

    """
    allowed_methods = ('GET',)
    model = Tag
    fields = ['name', 'href', 'url', 'slug']

    @piwik_track
    def read(self, request, category=None, pk=None):
        """ Lists all tags in the category (eg. all themes). """
        if pk is not None:
            # FIXME: Unused?
            try:
                return Tag.objects.exclude(category='set').get(pk=pk)
            except Book.DoesNotExist:
                return rc.NOT_FOUND

        try:
            category_sng = category_singular[category]
        except KeyError:
            return rc.NOT_FOUND

        after = request.GET.get('after')
        count = request.GET.get('count')

        tags = Tag.objects.filter(category=category_sng).exclude(items=None).order_by('slug')

        book_only = request.GET.get('book_only') == 'true'
        picture_only = request.GET.get('picture_only') == 'true'
        if book_only:
            tags = tags.filter(for_books=True)
        if picture_only:
            tags = tags.filter(for_pictures=True)

        if after:
            tags = tags.filter(slug__gt=after)

        if count:
            tags = tags[:count]

        return tags


class FragmentDetails(object):
    """Custom Fragment fields."""

    @classmethod
    def href(cls, fragment):
        """ Returns URI in the API for the fragment. """

        return API_BASE + reverse("api_fragment", args=[fragment.book.slug, fragment.anchor])

    @classmethod
    def url(cls, fragment):
        """ Returns URL on the site for the fragment. """

        return WL_BASE + fragment.get_absolute_url()

    @classmethod
    def themes(cls, fragment):
        """ Returns a list of theme tags for the fragment. """

        return fragment.tags.filter(category='theme')


class FragmentDetailHandler(BaseHandler, FragmentDetails):
    fields = ['book', 'anchor', 'text', 'url', 'themes']

    @piwik_track
    def read(self, request, book, anchor):
        """ Returns details of a fragment, identified by book slug and anchor. """
        try:
            return Fragment.objects.get(book__slug=book, anchor=anchor)
        except Fragment.DoesNotExist:
            return rc.NOT_FOUND


class FragmentsHandler(BaseHandler, FragmentDetails):
    """ Main handler for Fragments.

    Responsible for lists of Fragment objects
    and fields used for representing Fragments.

    """
    model = Fragment
    fields = ['book', 'url', 'anchor', 'href']
    allowed_methods = ('GET',)

    categories = {'author', 'epoch', 'kind', 'genre', 'book', 'theme'}

    @piwik_track
    def read(self, request, tags):
        """ Lists all fragments with given book, tags, themes.

        :param tags: should be a path of categories and slugs, i.e.:
             books/book-slug/authors/an-author/themes/a-theme/

        """
        try:
            tags, ancestors = read_tags(tags, request, allowed=self.categories)
        except ValueError:
            return rc.NOT_FOUND
        fragments = Fragment.tagged.with_all(tags).select_related('book')
        if fragments.exists():
            return fragments
        else:
            return rc.NOT_FOUND


class PictureHandler(BaseHandler):
    model = Picture
    fields = ('slug', 'title')
    allowed_methods = ('POST',)

    def create(self, request):
        if not request.user.has_perm('picture.add_picture'):
            return rc.FORBIDDEN

        data = json.loads(request.POST.get('data'))
        form = PictureImportForm(data)
        if form.is_valid():
            form.save()
            return rc.CREATED
        else:
            return rc.NOT_FOUND


class UserDataHandler(BaseHandler):
    model = BookUserData
    fields = ('state', 'username', 'premium')
    allowed_methods = ('GET', 'POST')

    def read(self, request, slug=None):
        if not request.user.is_authenticated():
            return rc.FORBIDDEN
        if slug is None:
            return {'username': request.user.username, 'premium': user_is_subscribed(request.user)}
        try:
            book = Book.objects.get(slug=slug)
        except Book.DoesNotExist:
            return rc.NOT_FOUND
        try:
            data = BookUserData.objects.get(book=book, user=request.user)
        except BookUserData.DoesNotExist:
            return {'state': 'not_started'}
        return data

    def create(self, request, slug, state):
        try:
            book = Book.objects.get(slug=slug)
        except Book.DoesNotExist:
            return rc.NOT_FOUND
        if not request.user.is_authenticated():
            return rc.FORBIDDEN
        if state not in ('reading', 'complete'):
            return rc.NOT_FOUND
        data, created = BookUserData.objects.get_or_create(book=book, user=request.user)
        data.state = state
        data.save()
        return data


class UserShelfHandler(BookDetailHandler):
    fields = book_list_fields + ['liked']

    # FIXME: Unused?
    def parse_bool(self, s):
        if s in ('true', 'false'):
            return s == 'true'
        else:
            return None

    # hack, because piston is stupid
    @classmethod
    def liked(cls, book):
        return getattr(book, 'liked', None)

    def read(self, request, state):
        if not request.user.is_authenticated():
            return rc.FORBIDDEN
        likes = set(Book.tagged.with_any(request.user.tag_set.all()).values_list('id', flat=True))
        if state not in ('reading', 'complete', 'likes'):
            return rc.NOT_FOUND
        new_api = request.GET.get('new_api')
        after = request.GET.get('after')
        count = int(request.GET.get('count', 50))
        if state == 'likes':
            books = Book.tagged.with_any(request.user.tag_set.all())
        else:
            ids = BookUserData.objects.filter(user=request.user, complete=state == 'complete')\
                .values_list('book_id', flat=True)
            books = Book.objects.filter(id__in=list(ids)).distinct()
            books = self.order_books(books, new_api)
        if after:
            books = self.books_after(books, after, new_api)
        if count:
            books = books[:count]
        new_books = []
        for book in books:
            new_books.append(BookProxy(book).set('liked', book.id in likes))
        return QuerySetProxy(new_books)


class UserLikeHandler(BaseHandler):
    fields = []
    allowed_methods = ('GET', 'POST')

    def read(self, request, slug):
        if not request.user.is_authenticated():
            return rc.FORBIDDEN
        try:
            book = Book.objects.get(slug=slug)
        except Book.DoesNotExist:
            return rc.NOT_FOUND
        return {'likes': likes(request.user, book)}

    def create(self, request, slug):
        if not request.user.is_authenticated():
            return rc.FORBIDDEN
        try:
            book = Book.objects.get(slug=slug)
        except Book.DoesNotExist:
            return rc.NOT_FOUND
        action = request.GET.get('action', 'like')
        if action == 'like':
            book.like(request.user)
        elif action == 'unlike':
            book.unlike(request.user)
        return {}


class BlogEntryHandler(BaseHandler):
    model = Entry
    fields = (
        'title', 'lead', 'body', 'place', 'time', 'image_url', 'image_thumb', 'gallery_urls', 'type', 'key', 'url')

    def read(self, request):
        after = request.GET.get('after')
        count = int(request.GET.get('count', 20))
        entries = Entry.published_objects.filter(in_stream=True).order_by('-first_published_at')
        if after:
            entries = entries.filter(first_published_at__lt=after)
        if count:
            entries = entries[:count]
        return entries

    @classmethod
    def image_url(cls, entry):
        return (WL_BASE + entry.image.url) if entry.image else None

    @classmethod
    def image_thumb(cls, entry):
        return MEDIA_BASE + default.backend.get_thumbnail(
            entry.image, "193x193").url if entry.image else ''

    @classmethod
    def gallery_urls(cls, entry):
        return [WL_BASE + photo.url() for photo in entry.photo_set.all()]

    @classmethod
    def key(cls, entry):
        return entry.first_published_at

    @classmethod
    def url(cls, entry):
        return WL_BASE + entry.get_absolute_url()
