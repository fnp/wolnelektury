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
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from django.core.urlresolvers import reverse

from django.conf import settings

from newtagging.models import TagBase, tags_updated
from newtagging import managers
from catalogue.fields import JSONField

from librarian import dcparser, html, epub, NoDublinCore
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

MEDIA_FORMATS = (
    ('odt', _('ODT file')),
    ('mp3', _('MP3 file')),
    ('ogg', _('OGG file')),
    ('daisy', _('DAISY file')), 
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
    sort_key = models.CharField(_('sort key'), max_length=120, db_index=True)
    category = models.CharField(_('category'), max_length=50, blank=False, null=False,
        db_index=True, choices=TAG_CATEGORIES)
    description = models.TextField(_('description'), blank=True)
    main_page = models.BooleanField(_('main page'), default=False, db_index=True, help_text=_('Show tag on main page'))

    user = models.ForeignKey(User, blank=True, null=True)
    book_count = models.IntegerField(_('book count'), blank=False, null=True)
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

    def get_count(self):
        """ returns global book count for book tags, fragment count for themes """

        if self.book_count is None:
            if self.category == 'book':
                # never used
                objects = Book.objects.none()
            elif self.category == 'theme':
                objects = Fragment.tagged.with_all((self,))
            else:
                objects = Book.tagged.with_all((self,)).order_by()
                if self.category != 'set':
                    # eliminate descendants
                    l_tags = Tag.objects.filter(slug__in=[book.book_tag_slug() for book in objects])
                    descendants_keys = [book.pk for book in Book.tagged.with_any(l_tags)]
                    if descendants_keys:
                        objects = objects.exclude(pk__in=descendants_keys)
            self.book_count = objects.count()
            self.save()
        return self.book_count

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
def book_upload_path(ext=None):
    def get_dynamic_path(media, filename, ext=ext):
        # how to put related book's slug here?
        if not ext:
            ext = media.type
        if not media.name:
            name = slugify(filename.split(".")[0])
        else:
            name = slugify(media.name)
        return 'lektura/%s.%s' % (name, ext)
    return get_dynamic_path


class BookMedia(models.Model):
    type        = models.CharField(_('type'), choices=MEDIA_FORMATS, max_length="100")
    name        = models.CharField(_('name'), max_length="100", blank=True)
    file        = models.FileField(_('file'), upload_to=book_upload_path(), blank=True)    
    uploaded_at = models.DateTimeField(_('creation date'), auto_now_add=True, editable=False)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.file.name.split("/")[-1])

    class Meta:
        ordering            = ('type', 'name')
        verbose_name        = _('book media')
        verbose_name_plural = _('book media')

class Book(models.Model):
    title         = models.CharField(_('title'), max_length=120)
    slug          = models.SlugField(_('slug'), max_length=120, unique=True, db_index=True)
    description   = models.TextField(_('description'), blank=True)
    created_at    = models.DateTimeField(_('creation date'), auto_now_add=True)
    _short_html   = models.TextField(_('short HTML'), editable=False)
    parent_number = models.IntegerField(_('parent number'), default=0)
    extra_info    = JSONField(_('extra information'))
    gazeta_link   = models.CharField(blank=True, max_length=240)
    wiki_link     = models.CharField(blank=True, max_length=240)
    # files generated during publication
    xml_file      = models.FileField(_('XML file'), upload_to=book_upload_path('xml'), blank=True)
    html_file     = models.FileField(_('HTML file'), upload_to=book_upload_path('html'), blank=True)
    pdf_file      = models.FileField(_('PDF file'), upload_to=book_upload_path('pdf'), blank=True)
    epub_file     = models.FileField(_('EPUB file'), upload_to=book_upload_path('epub'), blank=True)    
    txt_file      = models.FileField(_('TXT file'), upload_to=book_upload_path('txt'), blank=True)        
    # other files
    medias        = models.ManyToManyField(BookMedia, blank=True)
    
    parent        = models.ForeignKey('self', blank=True, null=True, related_name='children')
    objects  = models.Manager()
    tagged   = managers.ModelTaggedItemManager(Tag)
    tags     = managers.TagDescriptor(Tag)

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

    def save(self, force_insert=False, force_update=False, reset_short_html=True, refresh_mp3=True, **kwargs):
        if reset_short_html:
            # Reset _short_html during save
            update = {}
            for key in filter(lambda x: x.startswith('_short_html'), self.__dict__):
                update[key] = ''
                self.__setattr__(key, '')
            # Fragment.short_html relies on book's tags, so reset it here too
            self.fragments.all().update(**update)

        book = super(Book, self).save(force_insert, force_update)

        if refresh_mp3 and self.has_media('mp3'):
            file = self.get_media('mp3')[0]
            #print file, file.path
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

    def has_media(self, type):
        if   type == 'xml':
            if self.xml_file:
                return True
            else:
                return False
        elif type == 'html':
            if self.html_file:
                return True
            else:
                return False        
        elif type == 'txt':
            if self.txt_file:
                return True
            else:
                return False        
        elif type == 'pdf':
            if self.pdf_file:
                return True
            else:
                return False  
        elif type == 'epub':
            if self.epub_file:
                return True
            else:
                return False                          
        else:
            if self.medias.filter(book=self, type=type).count() > 0:
                return True
            else:
                return False

    def get_media(self, type):
        if self.has_media(type):
            if   type == "xml":
                return self.xml_file
            elif type == "html":
                return self.html_file
            elif type == "epub":
                return self.html_file                
            elif type == "txt":
                return self.txt_file
            elif type == "pdf":
                return self.pdf_file
            else:                                             
                return self.medias.filter(book=self, type=type)
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

    def short_html(self):
        key = '_short_html_%s' % get_language()
        short_html = getattr(self, key)

        if short_html and len(short_html):
            return mark_safe(short_html)
        else:
            tags = self.tags.filter(~Q(category__in=('set', 'theme', 'book')))
            tags = [mark_safe(u'<a href="%s">%s</a>' % (tag.get_absolute_url(), tag.name)) for tag in tags]

            formats = []
            # files generated during publication               
            if self.has_media("html"):
                formats.append(u'<a href="%s">%s</a>' % (reverse('book_text', kwargs={'slug': self.slug}), _('Read online')))
            if self.has_media("pdf"):
                formats.append(u'<a href="%s">PDF</a>' % self.get_media('pdf').url)
            if self.root_ancestor.has_media("epub"):
                formats.append(u'<a href="%s">EPUB</a>' % self.root_ancestor.get_media('epub').url)
            if self.has_media("odt"):
                formats.append(u'<a href="%s">ODT</a>' % self.get_media('odt').url)
            if self.has_media("txt"):
                formats.append(u'<a href="%s">TXT</a>' % self.get_media('txt').url)
            # other files
            for m in self.medias.order_by('type'):
                formats.append(u'<a href="%s">%s</a>' % m.type, m.file.url)

            formats = [mark_safe(format) for format in formats]

            setattr(self, key, unicode(render_to_string('catalogue/book_short.html',
                {'book': self, 'tags': tags, 'formats': formats})))
            self.save(reset_short_html=False)
            return mark_safe(getattr(self, key))


    @property
    def root_ancestor(self):
        """ returns the oldest ancestor """

        if not hasattr(self, '_root_ancestor'):
            book = self
            while book.parent:
                book = book.parent
            self._root_ancestor = book
        return self._root_ancestor


    def get_mp3_info(self):
        """Retrieves artist and director names from audio ID3 tags."""
        audio = id3.ID3(self.get_media('mp3')[0].file.path)
        artist_name = ', '.join(', '.join(tag.text) for tag in audio.getall('TPE1'))
        director_name = ', '.join(', '.join(tag.text) for tag in audio.getall('TPE3'))
        return {'artist_name': artist_name, 'director_name': director_name}

    def has_description(self):
        return len(self.description) > 0
    has_description.short_description = _('description')
    has_description.boolean = True

    # ugly ugly ugly
    def has_pdf_file(self):
        return bool(self.pdf_file)
    has_pdf_file.short_description = 'PDF'
    has_pdf_file.boolean = True

    def has_epub_file(self):
        return bool(self.epub_file)
    has_epub_file.short_description = 'EPUB'
    has_epub_file.boolean = True

    def has_html_file(self):
        return bool(self.html_file)
    has_html_file.short_description = 'HTML'
    has_html_file.boolean = True

    def has_odt_file(self):
        return bool(self.has_media("odt"))
    has_odt_file.short_description = 'ODT'
    has_odt_file.boolean = True

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
    
    def build_epub(self, remove_descendants=True):
        """ (Re)builds the epub file.
            If book has a parent, does nothing.
            Unless remove_descendants is False, descendants' epubs are removed.
        """
    
        from StringIO import StringIO
        from hashlib import sha1
        from django.core.files.base import ContentFile
        from librarian import DocProvider

        class BookImportDocProvider(DocProvider):
            """ used for joined EPUBs """

            def __init__(self, book):
                self.book = book

            def by_slug(self, slug):
                if slug == self.book.slug:
                    return self.book.xml_file
                else:
                    return Book.objects.get(slug=slug).xml_file

        if self.parent:
            # don't need an epub
            return

        epub_file = StringIO()
        try:
            epub.transform(BookImportDocProvider(self), self.slug, epub_file)
            self.epub_file.save('%s.epub' % self.slug, ContentFile(epub_file.getvalue()), save=False)
            self.save(refresh_mp3=False)
            FileRecord(slug=self.slug, type='epub', sha1=sha1(epub_file.getvalue()).hexdigest()).save()
        except NoDublinCore:
            pass

        book_descendants = list(self.children.all())
        while len(book_descendants) > 0:
            child_book = book_descendants.pop(0)
            if remove_descendants and child_book.has_epub_file():
                child_book.epub_file.delete()
            # save anyway, to refresh short_html
            child_book.save(refresh_mp3=False)
            book_descendants += list(child_book.children.all())


    @classmethod
    def from_xml_file(cls, xml_file, overwrite=False):
        # use librarian to parse meta-data
        book_info = dcparser.parse(xml_file)

        if not isinstance(xml_file, File):
            xml_file = File(open(xml_file))

        try:
            return cls.from_text_and_meta(xml_file, book_info, overwrite)
        finally:
            xml_file.close()

    @classmethod
    def from_text_and_meta(cls, raw_file, book_info, overwrite=False):
        from tempfile import NamedTemporaryFile
        from slughifi import slughifi
        from markupstring import MarkupString
        from django.core.files.storage import default_storage

        # check for parts before we do anything
        children = []
        if hasattr(book_info, 'parts'):
            for part_url in book_info.parts:
                base, slug = part_url.rsplit('/', 1)
                try:
                    children.append(Book.objects.get(slug=slug))
                except Book.DoesNotExist, e:
                    raise Book.DoesNotExist(_('Book with slug = "%s" does not exist.') % slug)


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
        categories = (('kinds', 'kind'), ('genres', 'genre'), ('authors', 'author'), ('epochs', 'epoch'))
        for field_name, category in categories:
            try:
                tag_names = getattr(book_info, field_name)
            except:
                tag_names = [getattr(book_info, category)]
            for tag_name in tag_names:
                tag_sort_key = tag_name
                if category == 'author':
                    tag_sort_key = tag_name.last_name
                    tag_name = ' '.join(tag_name.first_names) + ' ' + tag_name.last_name
                tag, created = Tag.objects.get_or_create(slug=slughifi(tag_name), category=category)
                if created:
                    tag.name = tag_name
                    tag.sort_key = tag_sort_key.lower()
                    tag.save()
                book_tags.append(tag)

        book.tags = book_tags + book_shelves

        book_tag = book.book_tag()

        for n, child_book in enumerate(children):
            child_book.parent = book
            child_book.parent_number = n
            child_book.save()

        # Save XML and HTML files
        book.xml_file.save('%s.xml' % book.slug, raw_file, save=False)

        # delete old fragments when overwriting
        book.fragments.all().delete()

        html_file = NamedTemporaryFile()
        if html.transform(book.xml_file.path, html_file, parse_dublincore=False):
            book.html_file.save('%s.html' % book.slug, File(html_file), save=False)

            # get ancestor l-tags for adding to new fragments
            ancestor_tags = []
            p = book.parent
            while p:
                ancestor_tags.append(p.book_tag())
                p = p.parent

            # Extract fragments
            closed_fragments, open_fragments = html.extract_fragments(book.html_file.path)
            for fragment in closed_fragments.values():
                try:
                    theme_names = [s.strip() for s in fragment.themes.split(',')]
                except AttributeError:
                    continue
                themes = []
                for theme_name in theme_names:
                    if not theme_name:
                        continue
                    tag, created = Tag.objects.get_or_create(slug=slughifi(theme_name), category='theme')
                    if created:
                        tag.name = theme_name
                        tag.sort_key = theme_name.lower()
                        tag.save()
                    themes.append(tag)
                if not themes:
                    continue

                text = fragment.to_string()
                short_text = ''
                if (len(MarkupString(text)) > 240):
                    short_text = unicode(MarkupString(text)[:160])
                new_fragment, created = Fragment.objects.get_or_create(anchor=fragment.id, book=book,
                    defaults={'text': text, 'short_text': short_text})

                new_fragment.save()
                new_fragment.tags = set(book_tags + themes + [book_tag] + ancestor_tags)

        if not settings.NO_BUILD_EPUB:
            book.root_ancestor().build_epub()

        book_descendants = list(book.children.all())
        # add l-tag to descendants and their fragments
        # delete unnecessary EPUB files
        while len(book_descendants) > 0:
            child_book = book_descendants.pop(0)
            child_book.tags = list(child_book.tags) + [book_tag]
            child_book.save()
            for fragment in child_book.fragments.all():
                fragment.tags = set(list(fragment.tags) + [book_tag])
            book_descendants += list(child_book.children.all())

        # refresh cache
        book.reset_tag_counter()
        book.reset_theme_counter()

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

    def reset_tag_counter(self):
        self._tag_counter = None
        self.save(reset_short_html=False, refresh_mp3=False)
        if self.parent:
            self.parent.reset_tag_counter()

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

    def reset_theme_counter(self):
        self._theme_counter = None
        self.save(reset_short_html=False, refresh_mp3=False)
        if self.parent:
            self.parent.reset_theme_counter()

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


class FileRecord(models.Model):
    slug = models.SlugField(_('slug'), max_length=120, db_index=True)
    type = models.CharField(_('type'), max_length=20, db_index=True)
    sha1 = models.CharField(_('sha-1 hash'), max_length=40)
    time = models.DateTimeField(_('time'), auto_now_add=True)

    class Meta:
        ordering = ('-time','-slug', '-type')
        verbose_name = _('file record')
        verbose_name_plural = _('file records')

    def __unicode__(self):
        return "%s %s.%s" % (self.sha1,  self.slug, self.type)


def _tags_updated_handler(sender, affected_tags, **kwargs):
    # reset tag global counter
    Tag.objects.filter(pk__in=[tag.pk for tag in affected_tags]).update(book_count=None)

    # if book tags changed, reset book tag counter
    if isinstance(sender, Book) and \
                Tag.objects.filter(pk__in=(tag.pk for tag in affected_tags)).\
                    exclude(category__in=('book', 'theme', 'set')).count():
        sender.reset_tag_counter()
    # if fragment theme changed, reset book theme counter
    elif isinstance(sender, Fragment) and \
                Tag.objects.filter(pk__in=(tag.pk for tag in affected_tags)).\
                    filter(category='theme').count():
        sender.book.reset_theme_counter()
tags_updated.connect(_tags_updated_handler)

