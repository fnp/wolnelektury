# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.

from datetime import datetime, timedelta
import json

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from piston.handler import AnonymousBaseHandler, BaseHandler
from piston.utils import rc

from api.helpers import timestamp
from api.models import Deleted
from catalogue.forms import BookImportForm
from catalogue.models import Book, Tag, BookMedia, Fragment
from picture.models import Picture
from picture.forms import PictureImportForm

from stats.utils import piwik_track

API_BASE = WL_BASE = MEDIA_BASE = 'http://' + Site.objects.get_current().domain


category_singular = {
    'authors': 'author',
    'kinds': 'kind',
    'genres': 'genre',
    'epochs': 'epoch',
    'themes': 'theme',
    'books': 'book',
}
category_plural={}
for k, v in category_singular.items():
    category_plural[v] = k


def read_tags(tags, allowed):
    """ Reads a path of filtering tags.

    :param str tags: a path of category and slug pairs, like: authors/an-author/...
    :returns: list of Tag objects
    :raises: ValueError when tags can't be found
    """
    if not tags:
        return []

    tags = tags.strip('/').split('/')
    real_tags = []
    while tags:
        category = tags.pop(0)
        slug = tags.pop(0)

        try:
            category = category_singular[category]
        except KeyError:
            raise ValueError('Unknown category.')

        if not category in allowed:
            raise ValueError('Category not allowed.')

        # !^%@#$^#!
        if category == 'book':
            slug = 'l-' + slug

        try:
            real_tags.append(Tag.objects.get(category=category, slug=slug))
        except Tag.DoesNotExist:
            raise ValueError('Tag not found')
    return real_tags


# RESTful handlers


class BookMediaHandler(BaseHandler):
    """ Responsible for representing media in Books. """

    model = BookMedia
    fields = ['name', 'type', 'url']

    @classmethod
    def url(cls, media):
        """ Link to media on site. """

        return MEDIA_BASE + media.file.url


class BookDetailHandler(BaseHandler):
    """ Main handler for Book objects.

    Responsible for lists of Book objects
    and fields used for representing Books.

    """
    allowed_methods = ['GET']
    fields = ['title', 'parent'] + Book.formats + [
        'media', 'url'] + category_singular.keys()

    @piwik_track
    def read(self, request, slug):
        """ Returns details of a book, identified by a slug and lang. """
        try:
            return Book.objects.get(slug=slug)
        except Book.DoesNotExist:
            return rc.NOT_FOUND


class AnonymousBooksHandler(AnonymousBaseHandler):
    """ Main handler for Book objects.

    Responsible for lists of Book objects
    and fields used for representing Books.

    """
    allowed_methods = ('GET',)
    model = Book
    fields = ['href', 'title']

    categories = set(['author', 'epoch', 'kind', 'genre'])

    @classmethod
    def href(cls, book):
        """ Returns an URI for a Book in the API. """
        return API_BASE + reverse("api_book", args=[book.slug])

    @classmethod
    def url(cls, book):
        """ Returns Book's URL on the site. """

        return WL_BASE + book.get_absolute_url()

    @piwik_track
    def read(self, request, tags, top_level=False):
        """ Lists all books with given tags.

        :param tags: filtering tags; should be a path of categories
             and slugs, i.e.: authors/an-author/epoch/an-epoch/
        :param top_level: if True and a book is included in the results,
             it's children are aren't. By default all books matching the tags
             are returned.
        """
        tags = read_tags(tags, allowed=self.categories)
        if tags:
            if top_level:
                books = Book.tagged_top_level(tags)
                return books if books else rc.NOT_FOUND
            else:
                books = Book.tagged.with_all(tags)
        else:
            books = Book.objects.all()

        if books.exists():
            return books
        else:
            return rc.NOT_FOUND

    def create(self, request, tags, top_level=False):
        return 'aaa'

    @classmethod
    def media(self, book):
        """ Returns all media for a book. """

        return book.media.all()


class BooksHandler(BaseHandler):
    model = Book
    fields = ('slug', 'title')
    anonymous = AnonymousBooksHandler

    def create(self, request, tags, top_level=False):
        if not request.user.has_perm('catalogue.add_book'):
            return rc.FORBIDDEN

        data = json.loads(request.POST.get('data'))
        form = BookImportForm(data)
        if form.is_valid():
            form.save()
            return rc.CREATED
        else:
            return rc.NOT_FOUND

# add categorized tags fields for Book
def _tags_getter(category):
    @classmethod
    def get_tags(cls, book):
        return book.tags.filter(category=category)
    return get_tags
for plural, singular in category_singular.items():
    setattr(BooksHandler, plural, _tags_getter(singular))

# add fields for files in Book
def _file_getter(format):
    field = "%s_file" % format
    @classmethod
    def get_file(cls, book):
        f = getattr(book, field)
        if f:
            return MEDIA_BASE + f.url
        else:
            return ''
    return get_file
for format in Book.formats:
    setattr(BooksHandler, format, _file_getter(format))


class TagDetailHandler(BaseHandler):
    """ Responsible for details of a single Tag object. """

    fields = ['name', 'sort_key', 'description']

    @piwik_track
    def read(self, request, category, slug):
        """ Returns details of a tag, identified by category and slug. """

        try:
            category_sng = category_singular[category]
        except KeyError, e:
            return rc.NOT_FOUND

        try:
            return Tag.objects.get(category=category_sng, slug=slug)
        except Tag.DoesNotExist:
            return rc.NOT_FOUND


class TagsHandler(BaseHandler):
    """ Main handler for Tag objects.

    Responsible for lists of Tag objects
    and fields used for representing Tags.

    """
    allowed_methods = ('GET',)
    model = Tag
    fields = ['name', 'href']

    @piwik_track
    def read(self, request, category):
        """ Lists all tags in the category (eg. all themes). """

        try:
            category_sng = category_singular[category]
        except KeyError, e:
            return rc.NOT_FOUND

        tags = Tag.objects.filter(category=category_sng).exclude(book_count=0)
        if tags.exists():
            return tags
        else:
            return rc.NOT_FOUND


    @classmethod
    def href(cls, tag):
        """ Returns URI in the API for the tag. """

        return API_BASE + reverse("api_tag", args=[category_plural[tag.category], tag.slug])


class FragmentDetailHandler(BaseHandler):
    fields = ['book', 'anchor', 'text', 'url', 'themes']

    @piwik_track
    def read(self, request, slug, anchor):
        """ Returns details of a fragment, identified by book slug and anchor. """
        try:
            return Fragment.objects.get(book__slug=slug, anchor=anchor)
        except Fragment.DoesNotExist:
            return rc.NOT_FOUND


class FragmentsHandler(BaseHandler):
    """ Main handler for Fragments.

    Responsible for lists of Fragment objects
    and fields used for representing Fragments.

    """
    model = Fragment
    fields = ['book', 'anchor', 'href']
    allowed_methods = ('GET',)

    categories = set(['author', 'epoch', 'kind', 'genre', 'book', 'theme'])

    @piwik_track
    def read(self, request, tags):
        """ Lists all fragments with given book, tags, themes.

        :param tags: should be a path of categories and slugs, i.e.:
             books/book-slug/authors/an-author/themes/a-theme/

        """
        tags = read_tags(tags, allowed=self.categories)
        fragments = Fragment.tagged.with_all(tags).select_related('book')
        if fragments.exists():
            return fragments
        else:
            return rc.NOT_FOUND

    @classmethod
    def href(cls, fragment):
        """ Returns URI in the API for the fragment. """

        return API_BASE + reverse("api_fragment", 
            args=[fragment.book.slug, fragment.anchor])

    @classmethod
    def url(cls, fragment):
        """ Returns URL on the site for the fragment. """

        return WL_BASE + fragment.get_absolute_url()

    @classmethod
    def themes(cls, fragment):
        """ Returns a list of theme tags for the fragment. """

        return fragment.tags.filter(category='theme')




# Changes handlers

class CatalogueHandler(BaseHandler):

    @staticmethod
    def fields(request, name):
        fields_str = request.GET.get(name) if request is not None else None
        return fields_str.split(',') if fields_str is not None else None

    @staticmethod
    def until(t=None):
        """ Returns time suitable for use as upper time boundary for check.

            Used to avoid issues with time between setting the change stamp
            and actually saving the model in database.
            Cuts the microsecond part to avoid issues with DBs where time has
            more precision.

            :param datetime t: manually sets the upper boundary

        """
        # set to five minutes ago, to avoid concurrency issues
        if t is None:
            t = datetime.now() - timedelta(seconds=settings.API_WAIT)
        # set to whole second in case DB supports something smaller
        return t.replace(microsecond=0)

    @staticmethod
    def book_dict(book, fields=None):
        all_fields = ['url', 'title', 'description',
                      'gazeta_link', 'wiki_link',
                      ] + Book.formats + BookMedia.formats + [
                      'parent', 'parent_number',
                      'tags',
                      'license', 'license_description', 'source_name',
                      'technical_editors', 'editors',
                      'author', 'sort_key',
                     ]
        if fields:
            fields = (f for f in fields if f in all_fields)
        else:
            fields = all_fields

        extra_info = book.get_extra_info_value()

        obj = {}
        for field in fields:

            if field in Book.formats:
                f = getattr(book, field+'_file')
                if f:
                    obj[field] = {
                        'url': f.url,
                        'size': f.size,
                    }

            elif field in BookMedia.formats:
                media = []
                for m in book.media.filter(type=field):
                    media.append({
                        'url': m.file.url,
                        'size': m.file.size,
                    })
                if media:
                    obj[field] = media

            elif field == 'url':
                obj[field] = book.get_absolute_url()

            elif field == 'tags':
                obj[field] = [t.id for t in book.tags.exclude(category__in=('book', 'set'))]

            elif field == 'author':
                obj[field] = ", ".join(t.name for t in book.tags.filter(category='author'))

            elif field == 'parent':
                obj[field] = book.parent_id

            elif field in ('license', 'license_description', 'source_name',
                      'technical_editors', 'editors'):
                f = extra_info.get(field)
                if f:
                    obj[field] = f

            else:
                f = getattr(book, field)
                if f:
                    obj[field] = f

        obj['id'] = book.id
        return obj

    @classmethod
    def book_changes(cls, request=None, since=0, until=None, fields=None):
        since = datetime.fromtimestamp(int(since))
        until = cls.until(until)

        changes = {
            'time_checked': timestamp(until)
        }

        if not fields:
            fields = cls.fields(request, 'book_fields')

        added = []
        updated = []
        deleted = []

        last_change = since
        for book in Book.objects.filter(changed_at__gte=since,
                    changed_at__lt=until):
            book_d = cls.book_dict(book, fields)
            updated.append(book_d)
        if updated:
            changes['updated'] = updated

        for book in Deleted.objects.filter(content_type=Book, 
                    deleted_at__gte=since,
                    deleted_at__lt=until,
                    created_at__lt=since):
            deleted.append(book.id)
        if deleted:
            changes['deleted'] = deleted

        return changes

    @staticmethod
    def tag_dict(tag, fields=None):
        all_fields = ('name', 'category', 'sort_key', 'description',
                      'gazeta_link', 'wiki_link',
                      'url', 'books',
                     )

        if fields:
            fields = (f for f in fields if f in all_fields)
        else:
            fields = all_fields

        obj = {}
        for field in fields:

            if field == 'url':
                obj[field] = tag.get_absolute_url()

            elif field == 'books':
                obj[field] = [b.id for b in Book.tagged_top_level([tag])]

            elif field == 'sort_key':
                obj[field] = tag.sort_key

            else:
                f = getattr(tag, field)
                if f:
                    obj[field] = f

        obj['id'] = tag.id
        return obj

    @classmethod
    def tag_changes(cls, request=None, since=0, until=None, fields=None, categories=None):
        since = datetime.fromtimestamp(int(since))
        until = cls.until(until)

        changes = {
            'time_checked': timestamp(until)
        }

        if not fields:
            fields = cls.fields(request, 'tag_fields')
        if not categories:
            categories = cls.fields(request, 'tag_categories')

        all_categories = ('author', 'epoch', 'kind', 'genre')
        if categories:
            categories = (c for c in categories if c in all_categories)
        else:
            categories = all_categories

        updated = []
        deleted = []

        for tag in Tag.objects.filter(category__in=categories, 
                    changed_at__gte=since,
                    changed_at__lt=until):
            # only serve non-empty tags
            if tag.book_count:
                tag_d = cls.tag_dict(tag, fields)
                updated.append(tag_d)
            elif tag.created_at < since:
                deleted.append(tag.id)
        if updated:
            changes['updated'] = updated

        for tag in Deleted.objects.filter(category__in=categories,
                content_type=Tag, 
                    deleted_at__gte=since,
                    deleted_at__lt=until,
                    created_at__lt=since):
            deleted.append(tag.id)
        if deleted:
            changes['deleted'] = deleted

        return changes

    @classmethod
    def changes(cls, request=None, since=0, until=None, book_fields=None,
                tag_fields=None, tag_categories=None):
        until = cls.until(until)

        changes = {
            'time_checked': timestamp(until)
        }

        changes_by_type = {
            'books': cls.book_changes(request, since, until, book_fields),
            'tags': cls.tag_changes(request, since, until, tag_fields, tag_categories),
        }

        for model in changes_by_type:
            for field in changes_by_type[model]:
                if field == 'time_checked':
                    continue
                changes.setdefault(field, {})[model] = changes_by_type[model][field]
        return changes


class BookChangesHandler(CatalogueHandler):
    allowed_methods = ('GET',)

    @piwik_track
    def read(self, request, since):
        return self.book_changes(request, since)


class TagChangesHandler(CatalogueHandler):
    allowed_methods = ('GET',)

    @piwik_track
    def read(self, request, since):
        return self.tag_changes(request, since)


class ChangesHandler(CatalogueHandler):
    allowed_methods = ('GET',)

    @piwik_track
    def read(self, request, since):
        return self.changes(request, since)


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
