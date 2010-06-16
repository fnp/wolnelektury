# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.db.models import permalink, Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.files import File
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from django.core.urlresolvers import reverse
from datetime import datetime

from newtagging.models import TagBase
from newtagging import managers
from catalogue.fields import JSONField

from librarian import html, dcparser
from mutagen import id3


TAG_CATEGORIES = (
    ('author', _('author')),
    ('epoch', _('epoch')),
    ('kind', _('kind')),
    ('genre', _('genre')),
    ('theme', _('theme')),
    ('set', _('set')),
    ('book', _('book')),
)


class TagSubcategoryManager(models.Manager):
    def __init__(self, subcategory):
        super(TagSubcategoryManager, self).__init__()
        self.subcategory = subcategory

    def get_query_set(self):
        return super(TagSubcategoryManager, self).get_query_set().filter(category=self.subcategory)


class Tag(TagBase):
    name = models.CharField(_('name'), max_length=50, db_index=True)
    slug = models.SlugField(_('slug'), max_length=120, db_index=True)
    sort_key = models.SlugField(_('sort key'), max_length=120, db_index=True)
    category = models.CharField(_('category'), max_length=50, blank=False, null=False,
        db_index=True, choices=TAG_CATEGORIES)
    description = models.TextField(_('description'), blank=True)
    main_page = models.BooleanField(_('main page'), default=False, db_index=True, help_text=_('Show tag on main page'))

    user = models.ForeignKey(User, blank=True, null=True)
    book_count = models.IntegerField(_('book count'), default=0, blank=False, null=False)
    death = models.IntegerField(_(u'year of death'), blank=True, null=True)
    gazeta_link = models.CharField(blank=True, max_length=240)
    wiki_link = models.CharField(blank=True, max_length=240)

    categories_rev = {
        'autor': 'author',
        'epoka': 'epoch',
        'rodzaj': 'kind',
        'gatunek': 'genre',
        'motyw': 'theme',
        'polka': 'set',
    }
    categories_dict = dict((item[::-1] for item in categories_rev.iteritems()))

    class Meta:
        ordering = ('sort_key',)
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        unique_together = (("slug", "category"),)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "Tag(slug=%r)" % self.slug

    @permalink
    def get_absolute_url(self):
        return ('catalogue.views.tagged_object_list', [self.url_chunk])

    def has_description(self):
        return len(self.description) > 0
    has_description.short_description = _('description')
    has_description.boolean = True

    def alive(self):
        return self.death is None

    def in_pd(self):
        """ tests whether an author is in public domain """
        return self.death is not None and self.goes_to_pd() <= datetime.now().year

    def goes_to_pd(self):
        """ calculates the year of public domain entry for an author """
        return self.death + 71 if self.death is not None else None

    @staticmethod
    def get_tag_list(tags):
        if isinstance(tags, basestring):
            real_tags = []
            ambiguous_slugs = []
            category = None
            tags_splitted = tags.split('/')
            for index, name in enumerate(tags_splitted):
                if name in Tag.categories_rev:
                    category = Tag.categories_rev[name]
                else:
                    if category:
                        real_tags.append(Tag.objects.get(slug=name, category=category))
                        category = None
                    else:
                        try:
                            real_tags.append(Tag.objects.exclude(category='book').get(slug=name))
                        except Tag.MultipleObjectsReturned, e:
                            ambiguous_slugs.append(name)

            if category:
                # something strange left off
                raise Tag.DoesNotExist()
            if ambiguous_slugs:
                # some tags should be qualified
                e = Tag.MultipleObjectsReturned()
                e.tags = real_tags
                e.ambiguous_slugs = ambiguous_slugs
                raise e
            else:
                return real_tags
        else:
            return TagBase.get_tag_list(tags)

    @property
    def url_chunk(self):
        return '/'.join((Tag.categories_dict[self.category], self.slug))


# TODO: why is this hard-coded ?
def book_upload_path(ext):
    def get_dynamic_path(book, filename):
        return 'lektura/%s.%s' % (book.slug, ext)
    return get_dynamic_path


class Book(models.Model):
    title = models.CharField(_('title'), max_length=120)
    slug = models.SlugField(_('slug'), max_length=120, unique=True, db_index=True)
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(_('creation date'), auto_now=True)
    _short_html = models.TextField(_('short HTML'), editable=False)
    parent_number = models.IntegerField(_('parent number'), default=0)
    extra_info = JSONField(_('extra information'))
    gazeta_link = models.CharField(blank=True, max_length=240)
    wiki_link = models.CharField(blank=True, max_length=240)


    # Formats
    xml_file = models.FileField(_('XML file'), upload_to=book_upload_path('xml'), blank=True)
    html_file = models.FileField(_('HTML file'), upload_to=book_upload_path('html'), blank=True)
    pdf_file = models.FileField(_('PDF file'), upload_to=book_upload_path('pdf'), blank=True)
    epub_file = models.FileField(_('EPUB file'), upload_to=book_upload_path('epub'), blank=True)
    odt_file = models.FileField(_('ODT file'), upload_to=book_upload_path('odt'), blank=True)
    txt_file = models.FileField(_('TXT file'), upload_to=book_upload_path('txt'), blank=True)
    mp3_file = models.FileField(_('MP3 file'), upload_to=book_upload_path('mp3'), blank=True)
    ogg_file = models.FileField(_('OGG file'), upload_to=book_upload_path('ogg'), blank=True)

    parent = models.ForeignKey('self', blank=True, null=True, related_name='children')

    objects = models.Manager()
    tagged = managers.ModelTaggedItemManager(Tag)
    tags = managers.TagDescriptor(Tag)

    _tag_counter = JSONField(null=True, editable=False)
    _theme_counter = JSONField(null=True, editable=False)

    class AlreadyExists(Exception):
        pass

    class Meta:
        ordering = ('title',)
        verbose_name = _('book')
        verbose_name_plural = _('books')

    def __unicode__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, reset_short_html=True, refresh_mp3=True):
        if reset_short_html:
            # Reset _short_html during save
            update = {}
            for key in filter(lambda x: x.startswith('_short_html'), self.__dict__):
                update[key] = ''
                self.__setattr__(key, '')
            # Fragment.short_html relies on book's tags, so reset it here too
            self.fragments.all().update(**update)

        book = super(Book, self).save(force_insert, force_update)

        if refresh_mp3 and self.mp3_file:
            print self.mp3_file, self.mp3_file.path
            extra_info = self.get_extra_info_value()
            extra_info.update(self.get_mp3_info())
            self.set_extra_info_value(extra_info)
            book = super(Book, self).save(force_insert, force_update)

        return book

    @permalink
    def get_absolute_url(self):
        return ('catalogue.views.book_detail', [self.slug])

    @property
    def name(self):
        return self.title

    def book_tag(self):
        slug = ('l-' + self.slug)[:120]
        book_tag, created = Tag.objects.get_or_create(slug=slug, category='book')
        if created:
            book_tag.name = self.title[:50]
            book_tag.sort_key = slug
            book_tag.save()
        return book_tag

    def short_html(self):
        key = '_short_html_%s' % get_language()
        short_html = getattr(self, key)

        if short_html and len(short_html):
            return mark_safe(short_html)
        else:
            tags = self.tags.filter(~Q(category__in=('set', 'theme', 'book')))
            tags = [mark_safe(u'<a href="%s">%s</a>' % (tag.get_absolute_url(), tag.name)) for tag in tags]

            formats = []
            if self.html_file:
                formats.append(u'<a href="%s">%s</a>' % (reverse('book_text', kwargs={'slug': self.slug}), _('Read online')))
            if self.pdf_file:
                formats.append(u'<a href="%s">PDF</a>' % self.pdf_file.url)
            if self.epub_file:
                formats.append(u'<a href="%s">EPUB</a>' % self.epub_file.url)
            if self.odt_file:
                formats.append(u'<a href="%s">ODT</a>' % self.odt_file.url)
            if self.txt_file:
                formats.append(u'<a href="%s">TXT</a>' % self.txt_file.url)
            if self.mp3_file:
                formats.append(u'<a href="%s">MP3</a>' % self.mp3_file.url)
            if self.ogg_file:
                formats.append(u'<a href="%s">OGG</a>' % self.ogg_file.url)

            formats = [mark_safe(format) for format in formats]

            setattr(self, key, unicode(render_to_string('catalogue/book_short.html',
                {'book': self, 'tags': tags, 'formats': formats})))
            self.save(reset_short_html=False)
            return mark_safe(getattr(self, key))


    def get_mp3_info(self):
        """Retrieves artist and director names from audio ID3 tags."""
        audio = id3.ID3(self.mp3_file.path)
        artist_name = ', '.join(', '.join(tag.text) for tag in audio.getall('TPE1'))
        director_name = ', '.join(', '.join(tag.text) for tag in audio.getall('TPE3'))
        return {'artist_name': artist_name, 'director_name': director_name}

    def has_description(self):
        return len(self.description) > 0
    has_description.short_description = _('description')
    has_description.boolean = True

    def has_pdf_file(self):
        return bool(self.pdf_file)
    has_pdf_file.short_description = 'PDF'
    has_pdf_file.boolean = True

    def has_epub_file(self):
        return bool(self.epub_file)
    has_epub_file.short_description = 'EPUB'
    has_epub_file.boolean = True

    def has_odt_file(self):
        return bool(self.odt_file)
    has_odt_file.short_description = 'ODT'
    has_odt_file.boolean = True

    def has_html_file(self):
        return bool(self.html_file)
    has_html_file.short_description = 'HTML'
    has_html_file.boolean = True

    @classmethod
    def from_xml_file(cls, xml_file, overwrite=False):
        # use librarian to parse meta-data
        book_info = dcparser.parse(xml_file)

        if not isinstance(xml_file, File):
            xml_file = File(xml_file)

        try:
            return cls.from_text_and_meta(xml_file, book_info, overwrite)
        finally:
            xml_file.close()

    @classmethod
    def from_text_and_meta(cls, raw_file, book_info, overwrite=False):
        from tempfile import NamedTemporaryFile
        from slughifi import slughifi
        from markupstring import MarkupString

        # Read book metadata
        book_base, book_slug = book_info.url.rsplit('/', 1)
        book, created = Book.objects.get_or_create(slug=book_slug)

        if created:
            book_shelves = []
        else:
            if not overwrite:
                raise Book.AlreadyExists(_('Book %s already exists') % book_slug)
            # Save shelves for this book
            book_shelves = list(book.tags.filter(category='set'))

        book.title = book_info.title
        book.set_extra_info_value(book_info.to_dict())
        book._short_html = ''
        book.save()

        book_tags = []
        for category in ('kind', 'genre', 'author', 'epoch'):
            tag_name = getattr(book_info, category)
            tag_sort_key = tag_name
            if category == 'author':
                tag_sort_key = tag_name.last_name
                tag_name = ' '.join(tag_name.first_names) + ' ' + tag_name.last_name
            tag, created = Tag.objects.get_or_create(slug=slughifi(tag_name), category=category)
            if created:
                tag.name = tag_name
                tag.sort_key = slughifi(tag_sort_key)
                tag.save()
            book_tags.append(tag)

        book.tags = book_tags

        book_tag = book.book_tag()

        if hasattr(book_info, 'parts'):
            for n, part_url in enumerate(book_info.parts):
                base, slug = part_url.rsplit('/', 1)
                try:
                    child_book = Book.objects.get(slug=slug)
                    child_book.parent = book
                    child_book.parent_number = n
                    child_book.save()
                except Book.DoesNotExist, e:
                    raise Book.DoesNotExist(_('Book with slug = "%s" does not exist.') % slug)

        book_descendants = list(book.children.all())
        while len(book_descendants) > 0:
            child_book = book_descendants.pop(0)
            child_book.tags = list(child_book.tags) + [book_tag]
            child_book.save()
            for fragment in child_book.fragments.all():
                fragment.tags = set(list(fragment.tags) + [book_tag])
            book_descendants += list(child_book.children.all())

        # Save XML and HTML files
        book.xml_file.save('%s.xml' % book.slug, raw_file, save=False)

        html_file = NamedTemporaryFile()
        if html.transform(book.xml_file.path, html_file, parse_dublincore=False):
            book.html_file.save('%s.html' % book.slug, File(html_file), save=False)

            # Extract fragments
            closed_fragments, open_fragments = html.extract_fragments(book.html_file.path)
            book_themes = []
            for fragment in closed_fragments.values():
                text = fragment.to_string()
                short_text = ''
                if (len(MarkupString(text)) > 240):
                    short_text = unicode(MarkupString(text)[:160])
                new_fragment, created = Fragment.objects.get_or_create(anchor=fragment.id, book=book,
                    defaults={'text': text, 'short_text': short_text})

                try:
                    theme_names = [s.strip() for s in fragment.themes.split(',')]
                except AttributeError:
                    continue
                themes = []
                for theme_name in theme_names:
                    tag, created = Tag.objects.get_or_create(slug=slughifi(theme_name), category='theme')
                    if created:
                        tag.name = theme_name
                        tag.sort_key = slughifi(theme_name)
                        tag.save()
                    themes.append(tag)
                new_fragment.save()
                new_fragment.tags = set(list(book.tags) + themes + [book_tag])
                book_themes += themes

            book_themes = set(book_themes)
            book.tags = list(book.tags) + list(book_themes) + book_shelves

        book.save()
        return book


    def refresh_tag_counter(self):
        tags = {}
        for child in self.children.all().order_by():
            for tag_pk, value in child.tag_counter.iteritems():
                tags[tag_pk] = tags.get(tag_pk, 0) + value
        for tag in self.tags.exclude(category__in=('book', 'theme', 'set')).order_by():
            tags[tag.pk] = 1
        self.set__tag_counter_value(tags)
        self.save(reset_short_html=False, refresh_mp3=False)
        return tags

    @property
    def tag_counter(self):
        if self._tag_counter is None:
            return self.refresh_tag_counter()
        return dict((int(k), v) for k, v in self.get__tag_counter_value().iteritems())

    def refresh_theme_counter(self):
        tags = {}
        for fragment in Fragment.tagged.with_any([self.book_tag()]).order_by():
            for tag in fragment.tags.filter(category='theme').order_by():
                tags[tag.pk] = tags.get(tag.pk, 0) + 1
        self.set__theme_counter_value(tags)
        self.save(reset_short_html=False, refresh_mp3=False)
        return tags

    @property
    def theme_counter(self):
        if self._theme_counter is None:
            return self.refresh_theme_counter()
        return dict((int(k), v) for k, v in self.get__theme_counter_value().iteritems())



class Fragment(models.Model):
    text = models.TextField()
    short_text = models.TextField(editable=False)
    _short_html = models.TextField(editable=False)
    anchor = models.CharField(max_length=120)
    book = models.ForeignKey(Book, related_name='fragments')

    objects = models.Manager()
    tagged = managers.ModelTaggedItemManager(Tag)
    tags = managers.TagDescriptor(Tag)

    class Meta:
        ordering = ('book', 'anchor',)
        verbose_name = _('fragment')
        verbose_name_plural = _('fragments')

    def get_absolute_url(self):
        return '%s#m%s' % (reverse('book_text', kwargs={'slug': self.book.slug}), self.anchor)

    def short_html(self):
        key = '_short_html_%s' % get_language()
        short_html = getattr(self, key)
        if short_html and len(short_html):
            return mark_safe(short_html)
        else:
            setattr(self, key, unicode(render_to_string('catalogue/fragment_short.html',
                {'fragment': self})))
            self.save()
            return mark_safe(getattr(self, key))


class BookStub(models.Model):
    title = models.CharField(_('title'), max_length=120)
    author = models.CharField(_('author'), max_length=120)
    pd = models.IntegerField(_('goes to public domain'), null=True, blank=True)
    slug = models.SlugField(_('slug'), max_length=120, unique=True, db_index=True)
    translator = models.TextField(_('translator'), blank=True)
    translator_death = models.TextField(_('year of translator\'s death'), blank=True)

    class Meta:
        ordering = ('title',)
        verbose_name = _('book stub')
        verbose_name_plural = _('book stubs')

    def __unicode__(self):
        return self.title

    @permalink
    def get_absolute_url(self):
        return ('catalogue.views.book_detail', [self.slug])

    def in_pd(self):
        return self.pd is not None and self.pd <= datetime.now().year

    @property
    def name(self):
        return self.title


