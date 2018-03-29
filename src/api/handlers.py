# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.functional import lazy
from django.db import models
from piston.handler import AnonymousBaseHandler, BaseHandler
from piston.utils import rc
from sorl.thumbnail import default

from catalogue.forms import BookImportForm
from catalogue.models import Book, Tag, BookMedia, Fragment, Collection
from catalogue.models.tag import prefetch_relations
from picture.models import Picture
from picture.forms import PictureImportForm

from stats.utils import piwik_track
from wolnelektury.utils import re_escape

from . import emitters  # Register our emitters

API_BASE = WL_BASE = MEDIA_BASE = lazy(
    lambda: u'http://' + Site.objects.get_current().domain, unicode)()


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


def read_tags(tags, request, allowed):
    """ Reads a path of filtering tags.

    :param str tags: a path of category and slug pairs, like: authors/an-author/...
    :returns: list of Tag objects
    :raises: ValueError when tags can't be found
    """

    def process(category, slug):
        if category == 'book':
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


class BookDetailHandler(BaseHandler, BookDetails):
    """ Main handler for Book objects.

    Responsible for single Book details.
    """
    allowed_methods = ['GET']
    fields = ['title', 'parent', 'children'] + Book.formats + [
        'media', 'url', 'cover', 'cover_thumb', 'simple_thumb', 'simple_cover', 'fragment_data'] + [
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
    fields = book_tag_categories + ['href', 'title', 'url', 'cover', 'cover_thumb', 'slug', 'simple_thumb']

    @classmethod
    def genres(cls, book):
        """ Returns all media for a book. """
        return book.tags.filter(category='genre')

    @piwik_track
    def read(self, request, tags=None, top_level=False, audiobooks=False, daisy=False, pk=None,
             recommended=False, newest=False, books=None,
             after=None, before=None, count=None):
        """ Lists all books with given tags.

        :param tags: filtering tags; should be a path of categories
             and slugs, i.e.: authors/an-author/epoch/an-epoch/
        :param top_level: if True and a book is included in the results,
             it's children are aren't. By default all books matching the tags
             are returned.
        """
        if pk is not None:
            try:
                return Book.objects.get(pk=pk)
            except Book.DoesNotExist:
                return rc.NOT_FOUND

        try:
            tags, _ancestors = read_tags(tags, request, allowed=book_tag_categories)
        except ValueError:
            return rc.NOT_FOUND

        if 'after' in request.GET:
            after = request.GET['after']
        if 'before' in request.GET:
            before = request.GET['before']
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
        books = books.order_by('slug')

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
            books = books.filter(slug__gt=after)
        if before:
            books = books.filter(slug__lt=before)

        books = books.only('slug', 'title', 'cover', 'cover_thumb')
        for category in book_tag_categories:
            books = prefetch_relations(books, category)

        if count:
            if before:
                books = list(reversed(books.order_by('-slug')[:count]))
            else:
                books = books[:count]

        return books

    def create(self, request, *args, **kwargs):
        return rc.FORBIDDEN


class BooksHandler(BookDetailHandler):
    allowed_methods = ('GET', 'POST')
    model = Book
    fields = book_tag_categories + ['href', 'title', 'url', 'cover', 'cover_thumb', 'slug']
    anonymous = AnonymousBooksHandler

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


class EBooksHandler(AnonymousBooksHandler):
    fields = ('author', 'href', 'title', 'cover') + tuple(Book.ebook_formats) + ('slug',)


class BookProxy(models.Model):
    def __init__(self, book, key):
        self.book = book
        self.key = key

    def __getattr__(self, item):
        if item not in ('book', 'key'):
            return self.book.__getattribute__(item)
        else:
            return self.__getattribute__(item)


class QuerySetProxy(models.QuerySet):
    def __init__(self, l):
        self.list = l

    def __iter__(self):
        return iter(self.list)


class FilterBooksHandler(AnonymousBooksHandler):
    fields = book_tag_categories + [
        'href', 'title', 'url', 'cover', 'cover_thumb', 'simple_thumb', 'slug', 'key']

    def read(self, request):
        key_sep = '$'
        search_string = request.GET.get('search')
        is_lektura = request.GET.get('lektura')
        is_audiobook = request.GET.get('audiobook')

        after = request.GET.get('after')
        count = int(request.GET.get('count', 50))
        if is_lektura in ('true', 'false'):
            is_lektura = is_lektura == 'true'
        else:
            is_lektura = None
        if is_audiobook in ('true', 'false'):
            is_audiobook = is_audiobook == 'true'
        books = Book.objects.distinct().order_by('slug')
        if is_lektura is not None:
            books = books.filter(has_audience=is_lektura)
        if is_audiobook is not None:
            if is_audiobook:
                books = books.filter(media__type='mp3')
            else:
                books = books.exclude(media__type='mp3')
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
                which, slug = after.split(key_sep, 1)
                if which == 'title':
                    book_lists = [(books_title.filter(slug__gt=slug), 'title')]
                else:  # which == 'author'
                    book_lists = [(books_author.filter(slug__gt=slug), 'author'), (books_title, 'title')]
            else:
                book_lists = [(books_author, 'author'), (books_title, 'title')]
        else:
            if after and key_sep in after:
                which, slug = after.split(key_sep, 1)
                books = books.filter(slug__gt=slug)
            book_lists = [(books, 'book')]

        filtered_books = []
        for book_list, label in book_lists:
            book_list = book_list.only('slug', 'title', 'cover', 'cover_thumb')
            for category in book_tag_categories:
                book_list = prefetch_relations(book_list, category)
            remaining_count = count - len(filtered_books)
            new_books = [BookProxy(book, '%s%s%s' % (label, key_sep, book.slug))
                         for book in book_list[:remaining_count]]
            filtered_books += new_books
            if len(filtered_books) == count:
                break

        return QuerySetProxy(filtered_books)


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
    field = "%s_file" % book_format

    @classmethod
    def get_file(cls, book):
        f = getattr(book, field)
        if f:
            return MEDIA_BASE + f.url
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
            try:
                return Tag.objects.exclude(category='set').get(pk=pk)
            except Book.DoesNotExist:
                return rc.NOT_FOUND

        try:
            category_sng = category_singular[category]
        except KeyError:
            return rc.NOT_FOUND

        after = request.GET.get('after')
        before = request.GET.get('before')
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
        if before:
            tags = tags.filter(slug__lt=before)

        if count:
            if before:
                tags = list(reversed(tags.order_by('-slug')[:count]))
            else:
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
            tags, ancestors = read_tags(tags, allowed=self.categories)
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
