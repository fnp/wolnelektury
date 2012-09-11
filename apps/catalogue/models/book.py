# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import re
from django.conf import settings as settings
from django.core.cache import get_cache
from django.db import models
from django.db.models import permalink
import django.dispatch
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
import jsonfield
from catalogue import constants
from catalogue.fields import EbookField
from catalogue.models import Tag, Fragment, BookMedia
from catalogue.utils import create_zip, split_tags, book_upload_path
from catalogue import app_settings
from catalogue import tasks
from newtagging import managers


permanent_cache = get_cache('permanent')


class Book(models.Model):
    """Represents a book imported from WL-XML."""
    title         = models.CharField(_('title'), max_length=120)
    sort_key = models.CharField(_('sort key'), max_length=120, db_index=True, editable=False)
    slug = models.SlugField(_('slug'), max_length=120, db_index=True,
            unique=True)
    common_slug = models.SlugField(_('slug'), max_length=120, db_index=True)
    language = models.CharField(_('language code'), max_length=3, db_index=True,
                    default=app_settings.DEFAULT_LANGUAGE)
    description   = models.TextField(_('description'), blank=True)
    created_at    = models.DateTimeField(_('creation date'), auto_now_add=True, db_index=True)
    changed_at    = models.DateTimeField(_('creation date'), auto_now=True, db_index=True)
    parent_number = models.IntegerField(_('parent number'), default=0)
    extra_info    = jsonfield.JSONField(_('extra information'), default='{}')
    gazeta_link   = models.CharField(blank=True, max_length=240)
    wiki_link     = models.CharField(blank=True, max_length=240)
    # files generated during publication

    cover = EbookField('cover', _('cover'),
                upload_to=book_upload_path('jpg'), null=True, blank=True)
    ebook_formats = constants.EBOOK_FORMATS
    formats = ebook_formats + ['html', 'xml']

    parent = models.ForeignKey('self', blank=True, null=True,
        related_name='children')

    _related_info = jsonfield.JSONField(blank=True, null=True, editable=False)

    objects  = models.Manager()
    tagged   = managers.ModelTaggedItemManager(Tag)
    tags     = managers.TagDescriptor(Tag)

    html_built = django.dispatch.Signal()
    published = django.dispatch.Signal()

    class AlreadyExists(Exception):
        pass

    class Meta:
        ordering = ('sort_key',)
        verbose_name = _('book')
        verbose_name_plural = _('books')
        app_label = 'catalogue'

    def __unicode__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, reset_short_html=True, **kwargs):
        from sortify import sortify

        self.sort_key = sortify(self.title)

        ret = super(Book, self).save(force_insert, force_update)

        if reset_short_html:
            self.reset_short_html()

        return ret

    @permalink
    def get_absolute_url(self):
        return ('catalogue.views.book_detail', [self.slug])

    @property
    def name(self):
        return self.title

    def book_tag_slug(self):
        return ('l-' + self.slug)[:120]

    def book_tag(self):
        slug = self.book_tag_slug()
        book_tag, created = Tag.objects.get_or_create(slug=slug, category='book')
        if created:
            book_tag.name = self.title[:50]
            book_tag.sort_key = self.title.lower()
            book_tag.save()
        return book_tag

    def has_media(self, type_):
        if type_ in Book.formats:
            return bool(getattr(self, "%s_file" % type_))
        else:
            return self.media.filter(type=type_).exists()

    def get_media(self, type_):
        if self.has_media(type_):
            if type_ in Book.formats:
                return getattr(self, "%s_file" % type_)
            else:                                             
                return self.media.filter(type=type_)
        else:
            return None

    def get_mp3(self):
        return self.get_media("mp3")
    def get_odt(self):
        return self.get_media("odt")
    def get_ogg(self):
        return self.get_media("ogg")
    def get_daisy(self):
        return self.get_media("daisy")                       

    def reset_short_html(self):
        if self.id is None:
            return

        type(self).objects.filter(pk=self.pk).update(_related_info=None)
        # Fragment.short_html relies on book's tags, so reset it here too
        for fragm in self.fragments.all().iterator():
            fragm.reset_short_html()

    def has_description(self):
        return len(self.description) > 0
    has_description.short_description = _('description')
    has_description.boolean = True

    # ugly ugly ugly
    def has_mp3_file(self):
        return bool(self.has_media("mp3"))
    has_mp3_file.short_description = 'MP3'
    has_mp3_file.boolean = True

    def has_ogg_file(self):
        return bool(self.has_media("ogg"))
    has_ogg_file.short_description = 'OGG'
    has_ogg_file.boolean = True

    def has_daisy_file(self):
        return bool(self.has_media("daisy"))
    has_daisy_file.short_description = 'DAISY'
    has_daisy_file.boolean = True

    def wldocument(self, parse_dublincore=True, inherit=True):
        from catalogue.import_utils import ORMDocProvider
        from librarian.parser import WLDocument

        if inherit and self.parent:
            meta_fallbacks = self.parent.cover_info()
        else:
            meta_fallbacks = None

        return WLDocument.from_file(self.xml_file.path,
                provider=ORMDocProvider(self),
                parse_dublincore=parse_dublincore,
                meta_fallbacks=meta_fallbacks)

    @staticmethod
    def zip_format(format_):
        def pretty_file_name(book):
            return "%s/%s.%s" % (
                book.extra_info['author'],
                book.slug,
                format_)

        field_name = "%s_file" % format_
        books = Book.objects.filter(parent=None).exclude(**{field_name: ""})
        paths = [(pretty_file_name(b), getattr(b, field_name).path)
                    for b in books.iterator()]
        return create_zip(paths, app_settings.FORMAT_ZIPS[format_])

    def zip_audiobooks(self, format_):
        bm = BookMedia.objects.filter(book=self, type=format_)
        paths = map(lambda bm: (None, bm.file.path), bm)
        return create_zip(paths, "%s_%s" % (self.slug, format_))

    def search_index(self, book_info=None, index=None, index_tags=True, commit=True):
        import search
        if index is None:
            index = search.Index()
        try:
            index.index_book(self, book_info)
            if index_tags:
                index.index_tags()
            if commit:
                index.index.commit()
        except Exception, e:
            index.index.rollback()
            raise e


    @classmethod
    def from_xml_file(cls, xml_file, **kwargs):
        from django.core.files import File
        from librarian import dcparser

        # use librarian to parse meta-data
        book_info = dcparser.parse(xml_file)

        if not isinstance(xml_file, File):
            xml_file = File(open(xml_file))

        try:
            return cls.from_text_and_meta(xml_file, book_info, **kwargs)
        finally:
            xml_file.close()

    @classmethod
    def from_text_and_meta(cls, raw_file, book_info, overwrite=False,
            dont_build=None, search_index=True,
            search_index_tags=True):
        if dont_build is None:
            dont_build = set()
        dont_build = set.union(set(dont_build), set(app_settings.DONT_BUILD))

        # check for parts before we do anything
        children = []
        if hasattr(book_info, 'parts'):
            for part_url in book_info.parts:
                try:
                    children.append(Book.objects.get(slug=part_url.slug))
                except Book.DoesNotExist:
                    raise Book.DoesNotExist(_('Book "%s" does not exist.') %
                            part_url.slug)

        # Read book metadata
        book_slug = book_info.url.slug
        if re.search(r'[^a-z0-9-]', book_slug):
            raise ValueError('Invalid characters in slug')
        book, created = Book.objects.get_or_create(slug=book_slug)

        if created:
            book_shelves = []
            old_cover = None
        else:
            if not overwrite:
                raise Book.AlreadyExists(_('Book %s already exists') % (
                        book_slug))
            # Save shelves for this book
            book_shelves = list(book.tags.filter(category='set'))
            old_cover = book.cover_info()

        # Save XML file
        book.xml_file.save('%s.xml' % book.slug, raw_file, save=False)

        book.language = book_info.language
        book.title = book_info.title
        if book_info.variant_of:
            book.common_slug = book_info.variant_of.slug
        else:
            book.common_slug = book.slug
        book.extra_info = book_info.to_dict()
        book.save()

        meta_tags = Tag.tags_from_info(book_info)

        book.tags = set(meta_tags + book_shelves)

        cover_changed = old_cover != book.cover_info()
        obsolete_children = set(b for b in book.children.all()
                                if b not in children)
        notify_cover_changed = []
        for n, child_book in enumerate(children):
            new_child = child_book.parent != book
            child_book.parent = book
            child_book.parent_number = n
            child_book.save()
            if new_child or cover_changed:
                notify_cover_changed.append(child_book)
        # Disown unfaithful children and let them cope on their own.
        for child in obsolete_children:
            child.parent = None
            child.parent_number = 0
            child.save()
            tasks.fix_tree_tags.delay(child)
            if old_cover:
                notify_cover_changed.append(child)

        # delete old fragments when overwriting
        book.fragments.all().delete()
        # Build HTML, fix the tree tags, build cover.
        has_own_text = bool(book.html_file.build())
        tasks.fix_tree_tags.delay(book)
        if 'cover' not in dont_build:
            book.cover.build_delay()
        
        # No saves behind this point.

        if has_own_text:
            for format_ in constants.EBOOK_FORMATS_WITHOUT_CHILDREN:
                if format_ not in dont_build:
                    getattr(book, '%s_file' % format_).build_delay()
        for format_ in constants.EBOOK_FORMATS_WITH_CHILDREN:
            if format_ not in dont_build:
                getattr(book, '%s_file' % format_).build_delay()

        if not settings.NO_SEARCH_INDEX and search_index:
            tasks.index_book.delay(book.id, book_info=book_info, index_tags=search_index_tags)

        for child in notify_cover_changed:
            child.parent_cover_changed()

        cls.published.send(sender=book)
        return book

    def fix_tree_tags(self):
        """Fixes the l-tags on the book's subtree.

        Makes sure that:
        * the book has its parents book-tags,
        * its fragments have the book's and its parents book-tags,
        * runs those for every child book too,
        * touches all relevant tags,
        * resets tag and theme counter on the book and its ancestry.
        """
        def fix_subtree(book, parent_tags):
            affected_tags = set(book.tags)
            book.tags = list(book.tags.exclude(category='book')) + parent_tags
            sub_parent_tags = parent_tags + [book.book_tag()]
            for frag in book.fragments.all():
                affected_tags.update(frag.tags)
                frag.tags = list(frag.tags.exclude(category='book')
                                    ) + sub_parent_tags
            for child in book.children.all():
                affected_tags.update(fix_subtree(child, sub_parent_tags))
            return affected_tags

        parent_tags = []
        parent = self.parent
        while parent is not None:
            parent_tags.append(parent.book_tag())
            parent = parent.parent

        affected_tags = fix_subtree(self, parent_tags)
        for tag in affected_tags:
            tasks.touch_tag(tag)

        book = self
        while book is not None:
            book.reset_tag_counter()
            book.reset_theme_counter()
            book = book.parent

    def cover_info(self, inherit=True):
        """Returns a dictionary to serve as fallback for BookInfo.

        For now, the only thing inherited is the cover image.
        """
        need = False
        info = {}
        for field in ('cover_url', 'cover_by', 'cover_source'):
            val = self.extra_info.get(field)
            if val:
                info[field] = val
            else:
                need = True
        if inherit and need and self.parent is not None:
            parent_info = self.parent.cover_info()
            parent_info.update(info)
            info = parent_info
        return info

    def parent_cover_changed(self):
        """Called when parent book's cover image is changed."""
        if not self.cover_info(inherit=False):
            if 'cover' not in app_settings.DONT_BUILD:
                self.cover.build_delay()
            for format_ in constants.EBOOK_FORMATS_WITH_COVERS:
                if format_ not in app_settings.DONT_BUILD:
                    getattr(self, '%s_file' % format_).build_delay()
            for child in self.children.all():
                child.parent_cover_changed()

    def related_info(self):
        """Keeps info about related objects (tags, media) in cache field."""
        if self._related_info is not None:
            return self._related_info
        else:
            rel = {'tags': {}, 'media': {}}

            tags = self.tags.filter(category__in=(
                    'author', 'kind', 'genre', 'epoch'))
            tags = split_tags(tags)
            for category in tags:
                rel['tags'][category] = [
                        (t.name, t.slug) for t in tags[category]]

            for media_format in BookMedia.formats:
                rel['media'][media_format] = self.has_media(media_format)

            book = self
            parents = []
            while book.parent:
                parents.append((book.parent.title, book.parent.slug))
                book = book.parent
            parents = parents[::-1]
            if parents:
                rel['parents'] = parents

            if self.pk:
                type(self).objects.filter(pk=self.pk).update(_related_info=rel)
            return rel

    def related_themes(self):
        theme_counter = self.theme_counter
        book_themes = list(Tag.objects.filter(pk__in=theme_counter.keys()))
        for tag in book_themes:
            tag.count = theme_counter[tag.pk]
        return book_themes

    def reset_tag_counter(self):
        if self.id is None:
            return

        cache_key = "Book.tag_counter/%d" % self.id
        permanent_cache.delete(cache_key)
        if self.parent:
            self.parent.reset_tag_counter()

    @property
    def tag_counter(self):
        if self.id:
            cache_key = "Book.tag_counter/%d" % self.id
            tags = permanent_cache.get(cache_key)
        else:
            tags = None

        if tags is None:
            tags = {}
            for child in self.children.all().order_by().iterator():
                for tag_pk, value in child.tag_counter.iteritems():
                    tags[tag_pk] = tags.get(tag_pk, 0) + value
            for tag in self.tags.exclude(category__in=('book', 'theme', 'set')).order_by().iterator():
                tags[tag.pk] = 1

            if self.id:
                permanent_cache.set(cache_key, tags)
        return tags

    def reset_theme_counter(self):
        if self.id is None:
            return

        cache_key = "Book.theme_counter/%d" % self.id
        permanent_cache.delete(cache_key)
        if self.parent:
            self.parent.reset_theme_counter()

    @property
    def theme_counter(self):
        if self.id:
            cache_key = "Book.theme_counter/%d" % self.id
            tags = permanent_cache.get(cache_key)
        else:
            tags = None

        if tags is None:
            tags = {}
            for fragment in Fragment.tagged.with_any([self.book_tag()]).order_by().iterator():
                for tag in fragment.tags.filter(category='theme').order_by().iterator():
                    tags[tag.pk] = tags.get(tag.pk, 0) + 1

            if self.id:
                permanent_cache.set(cache_key, tags)
        return tags

    def pretty_title(self, html_links=False):
        book = self
        names = list(book.tags.filter(category='author'))

        books = []
        while book:
            books.append(book)
            book = book.parent
        names.extend(reversed(books))

        if html_links:
            names = ['<a href="%s">%s</a>' % (tag.get_absolute_url(), tag.name) for tag in names]
        else:
            names = [tag.name for tag in names]

        return ', '.join(names)

    @classmethod
    def tagged_top_level(cls, tags):
        """ Returns top-level books tagged with `tags`.

        It only returns those books which don't have ancestors which are
        also tagged with those tags.

        """
        # get relevant books and their tags
        objects = cls.tagged.with_all(tags)
        # eliminate descendants
        l_tags = Tag.objects.filter(category='book',
            slug__in=[book.book_tag_slug() for book in objects.iterator()])
        descendants_keys = [book.pk for book in cls.tagged.with_any(l_tags).iterator()]
        if descendants_keys:
            objects = objects.exclude(pk__in=descendants_keys)

        return objects

    @classmethod
    def book_list(cls, filter=None):
        """Generates a hierarchical listing of all books.

        Books are optionally filtered with a test function.

        """

        books_by_parent = {}
        books = cls.objects.all().order_by('parent_number', 'sort_key').only(
                'title', 'parent', 'slug')
        if filter:
            books = books.filter(filter).distinct()
            
            book_ids = set(b['pk'] for b in books.values("pk").iterator())
            for book in books.iterator():
                parent = book.parent_id
                if parent not in book_ids:
                    parent = None
                books_by_parent.setdefault(parent, []).append(book)
        else:
            for book in books.iterator():
                books_by_parent.setdefault(book.parent_id, []).append(book)

        orphans = []
        books_by_author = SortedDict()
        for tag in Tag.objects.filter(category='author').iterator():
            books_by_author[tag] = []

        for book in books_by_parent.get(None,()):
            authors = list(book.tags.filter(category='author'))
            if authors:
                for author in authors:
                    books_by_author[author].append(book)
            else:
                orphans.append(book)

        return books_by_author, orphans, books_by_parent

    _audiences_pl = {
        "SP1": (1, u"szkoła podstawowa"),
        "SP2": (1, u"szkoła podstawowa"),
        "P": (1, u"szkoła podstawowa"),
        "G": (2, u"gimnazjum"),
        "L": (3, u"liceum"),
        "LP": (3, u"liceum"),
    }
    def audiences_pl(self):
        audiences = self.extra_info.get('audiences', [])
        audiences = sorted(set([self._audiences_pl[a] for a in audiences]))
        return [a[1] for a in audiences]

    def choose_fragment(self):
        tag = self.book_tag()
        fragments = Fragment.tagged.with_any([tag])
        if fragments.exists():
            return fragments.order_by('?')[0]
        elif self.parent:
            return self.parent.choose_fragment()
        else:
            return None


# add the file fields
for format_ in Book.formats:
    field_name = "%s_file" % format_
    EbookField(format_, _("%s file" % format_.upper()),
            upload_to=book_upload_path(format_),
            blank=True, default='').contribute_to_class(Book, field_name)
