# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from collections import OrderedDict
from datetime import date, timedelta
from random import randint
import os.path
import re
from urllib.request import urlretrieve
from django.conf import settings
from django.db import connection, models, transaction
import django.dispatch
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _, get_language
from django.utils.deconstruct import deconstructible
import jsonfield
from fnpdjango.storage import BofhFileSystemStorage

from librarian.cover import WLCover
from librarian.html import transform_abstrakt
from newtagging import managers
from catalogue import constants
from catalogue.fields import EbookField
from catalogue.models import Tag, Fragment, BookMedia
from catalogue.utils import create_zip, gallery_url, gallery_path, split_tags, get_random_hash
from catalogue.models.tag import prefetched_relations
from catalogue import app_settings
from catalogue import tasks
from wolnelektury.utils import makedirs, cached_render, clear_cached_renders

bofh_storage = BofhFileSystemStorage()


@deconstructible
class UploadToPath(object):
    def __init__(self, path):
        self.path = path

    def __call__(self, instance, filename):
        return self.path % instance.slug


_cover_upload_to = UploadToPath('book/cover/%s.jpg')
_cover_thumb_upload_to = UploadToPath('book/cover_thumb/%s.jpg')
_cover_api_thumb_upload_to = UploadToPath('book/cover_api_thumb/%s.jpg')
_simple_cover_upload_to = UploadToPath('book/cover_simple/%s.jpg')


def _ebook_upload_to(upload_path):
    return UploadToPath(upload_path)


class Book(models.Model):
    """Represents a book imported from WL-XML."""
    title = models.CharField(_('title'), max_length=32767)
    sort_key = models.CharField(_('sort key'), max_length=120, db_index=True, editable=False)
    sort_key_author = models.CharField(
        _('sort key by author'), max_length=120, db_index=True, editable=False, default=u'')
    slug = models.SlugField(_('slug'), max_length=120, db_index=True, unique=True)
    common_slug = models.SlugField(_('slug'), max_length=120, db_index=True)
    language = models.CharField(_('language code'), max_length=3, db_index=True, default=app_settings.DEFAULT_LANGUAGE)
    description = models.TextField(_('description'), blank=True)
    abstract = models.TextField(_('abstract'), blank=True)
    created_at = models.DateTimeField(_('creation date'), auto_now_add=True, db_index=True)
    changed_at = models.DateTimeField(_('change date'), auto_now=True, db_index=True)
    parent_number = models.IntegerField(_('parent number'), default=0)
    extra_info = jsonfield.JSONField(_('extra information'), default={})
    gazeta_link = models.CharField(blank=True, max_length=240)
    wiki_link = models.CharField(blank=True, max_length=240)
    print_on_demand = models.BooleanField(_('print on demand'), default=False)
    recommended = models.BooleanField(_('recommended'), default=False)
    audio_length = models.CharField(_('audio length'), blank=True, max_length=8)
    preview = models.BooleanField(_('preview'), default=False)
    preview_until = models.DateField(_('preview until'), blank=True, null=True)
    preview_key = models.CharField(max_length=32, blank=True, null=True)

    # files generated during publication
    cover = EbookField(
        'cover', _('cover'),
        null=True, blank=True,
        upload_to=_cover_upload_to,
        storage=bofh_storage, max_length=255)
    # Cleaner version of cover for thumbs
    cover_thumb = EbookField(
        'cover_thumb', _('cover thumbnail'),
        null=True, blank=True,
        upload_to=_cover_thumb_upload_to,
        max_length=255)
    cover_api_thumb = EbookField(
        'cover_api_thumb', _('cover thumbnail for mobile app'),
        null=True, blank=True,
        upload_to=_cover_api_thumb_upload_to,
        max_length=255)
    simple_cover = EbookField(
        'simple_cover', _('cover for mobile app'),
        null=True, blank=True,
        upload_to=_simple_cover_upload_to,
        max_length=255)
    ebook_formats = constants.EBOOK_FORMATS
    formats = ebook_formats + ['html', 'xml']

    parent = models.ForeignKey('self', models.CASCADE, blank=True, null=True, related_name='children')
    ancestor = models.ManyToManyField('self', blank=True, editable=False, related_name='descendant', symmetrical=False)

    cached_author = models.CharField(blank=True, max_length=240, db_index=True)
    has_audience = models.BooleanField(default=False)

    objects = models.Manager()
    tagged = managers.ModelTaggedItemManager(Tag)
    tags = managers.TagDescriptor(Tag)
    tag_relations = GenericRelation(Tag.intermediary_table_model)

    html_built = django.dispatch.Signal()
    published = django.dispatch.Signal()

    SORT_KEY_SEP = '$'

    class AlreadyExists(Exception):
        pass

    class Meta:
        ordering = ('sort_key_author', 'sort_key')
        verbose_name = _('book')
        verbose_name_plural = _('books')
        app_label = 'catalogue'

    def __str__(self):
        return self.title

    def get_initial(self):
        try:
            return re.search(r'\w', self.title, re.U).group(0)
        except AttributeError:
            return ''

    def authors(self):
        return self.tags.filter(category='author')

    def epochs(self):
        return self.tags.filter(category='epoch')

    def genres(self):
        return self.tags.filter(category='genre')

    def kinds(self):
        return self.tags.filter(category='kind')

    def tag_unicode(self, category):
        relations = prefetched_relations(self, category)
        if relations:
            return ', '.join(rel.tag.name for rel in relations)
        else:
            return ', '.join(self.tags.filter(category=category).values_list('name', flat=True))

    def tags_by_category(self):
        return split_tags(self.tags.exclude(category__in=('set', 'theme')))

    def author_unicode(self):
        return self.cached_author

    def kind_unicode(self):
        return self.tag_unicode('kind')

    def epoch_unicode(self):
        return self.tag_unicode('epoch')

    def genre_unicode(self):
        return self.tag_unicode('genre')

    def translator(self):
        translators = self.extra_info.get('translators')
        if not translators:
            return None
        if len(translators) > 3:
            translators = translators[:2]
            others = ' i inni'
        else:
            others = ''
        return ', '.join(u'\xa0'.join(reversed(translator.split(', ', 1))) for translator in translators) + others

    def cover_source(self):
        return self.extra_info.get('cover_source', self.parent.cover_source() if self.parent else '')

    def save(self, force_insert=False, force_update=False, **kwargs):
        from sortify import sortify

        self.sort_key = sortify(self.title)[:120]
        self.title = str(self.title)  # ???

        try:
            author = self.authors().first().sort_key
        except AttributeError:
            author = u''
        self.sort_key_author = author

        self.cached_author = self.tag_unicode('author')
        self.has_audience = 'audience' in self.extra_info

        if self.preview and not self.preview_key:
            self.preview_key = get_random_hash(self.slug)[:32]

        ret = super(Book, self).save(force_insert, force_update, **kwargs)

        return ret

    def get_absolute_url(self):
        return reverse('book_detail', args=[self.slug])

    def gallery_path(self):
        return gallery_path(self.slug)

    def gallery_url(self):
        return gallery_url(self.slug)

    @property
    def name(self):
        return self.title

    def language_code(self):
        return constants.LANGUAGES_3TO2.get(self.language, self.language)

    def language_name(self):
        return dict(settings.LANGUAGES).get(self.language_code(), "")

    def is_foreign(self):
        return self.language_code() != settings.LANGUAGE_CODE

    def set_audio_length(self):
        length = self.get_audio_length()
        if length > 0:
            self.audio_length = self.format_audio_length(length)
            self.save()

    @staticmethod
    def format_audio_length(seconds):
        if seconds < 60*60:
            minutes = seconds // 60
            seconds = seconds % 60
            return '%d:%02d' % (minutes, seconds)
        else:
            hours = seconds // 3600
            minutes = seconds % 3600 // 60
            seconds = seconds % 60
            return '%d:%02d:%02d' % (hours, minutes, seconds)

    def get_audio_length(self):
        total = 0
        for media in self.get_mp3() or ():
            total += app_settings.GET_MP3_LENGTH(media.file.path)
        return int(total)

    def has_media(self, type_):
        if type_ in Book.formats:
            return bool(getattr(self, "%s_file" % type_))
        else:
            return self.media.filter(type=type_).exists()

    def has_audio(self):
        return self.has_media('mp3')

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

    def media_url(self, format_):
        media = self.get_media(format_)
        if media:
            if self.preview:
                return reverse('embargo_link', kwargs={'key': self.preview_key, 'slug': self.slug, 'format_': format_})
            else:
                return media.url
        else:
            return None

    def html_url(self):
        return self.media_url('html')

    def pdf_url(self):
        return self.media_url('pdf')

    def epub_url(self):
        return self.media_url('epub')

    def mobi_url(self):
        return self.media_url('mobi')

    def txt_url(self):
        return self.media_url('txt')

    def fb2_url(self):
        return self.media_url('fb2')

    def xml_url(self):
        return self.media_url('xml')

    def has_description(self):
        return len(self.description) > 0
    has_description.short_description = _('description')
    has_description.boolean = True

    def has_mp3_file(self):
        return self.has_media("mp3")
    has_mp3_file.short_description = 'MP3'
    has_mp3_file.boolean = True

    def has_ogg_file(self):
        return self.has_media("ogg")
    has_ogg_file.short_description = 'OGG'
    has_ogg_file.boolean = True

    def has_daisy_file(self):
        return self.has_media("daisy")
    has_daisy_file.short_description = 'DAISY'
    has_daisy_file.boolean = True

    def get_audiobooks(self):
        ogg_files = {}
        for m in self.media.filter(type='ogg').order_by().iterator():
            ogg_files[m.name] = m

        audiobooks = []
        projects = set()
        for mp3 in self.media.filter(type='mp3').iterator():
            # ogg files are always from the same project
            meta = mp3.extra_info
            project = meta.get('project')
            if not project:
                # temporary fallback
                project = u'CzytamySłuchając'

            projects.add((project, meta.get('funded_by', '')))

            media = {'mp3': mp3}

            ogg = ogg_files.get(mp3.name)
            if ogg:
                media['ogg'] = ogg
            audiobooks.append(media)

        projects = sorted(projects)
        return audiobooks, projects

    def wldocument(self, parse_dublincore=True, inherit=True):
        from catalogue.import_utils import ORMDocProvider
        from librarian.parser import WLDocument

        if inherit and self.parent:
            meta_fallbacks = self.parent.cover_info()
        else:
            meta_fallbacks = None

        return WLDocument.from_file(
            self.xml_file.path,
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
        books = Book.objects.filter(parent=None).exclude(**{field_name: ""}).exclude(preview=True)
        paths = [(pretty_file_name(b), getattr(b, field_name).path) for b in books.iterator()]
        return create_zip(paths, app_settings.FORMAT_ZIPS[format_])

    def zip_audiobooks(self, format_):
        bm = BookMedia.objects.filter(book=self, type=format_)
        paths = map(lambda bm: (None, bm.file.path), bm)
        return create_zip(paths, "%s_%s" % (self.slug, format_))

    def search_index(self, book_info=None, index=None, index_tags=True, commit=True):
        if index is None:
            from search.index import Index
            index = Index()
        try:
            index.index_book(self, book_info)
            if index_tags:
                index.index_tags()
            if commit:
                index.index.commit()
        except Exception as e:
            index.index.rollback()
            raise e

    # will make problems in conjunction with paid previews
    def download_pictures(self, remote_gallery_url):
        gallery_path = self.gallery_path()
        # delete previous files, so we don't include old files in ebooks
        if os.path.isdir(gallery_path):
            for filename in os.listdir(gallery_path):
                file_path = os.path.join(gallery_path, filename)
                os.unlink(file_path)
        ilustr_elements = list(self.wldocument().edoc.findall('//ilustr'))
        if ilustr_elements:
            makedirs(gallery_path)
            for ilustr in ilustr_elements:
                ilustr_src = ilustr.get('src')
                ilustr_path = os.path.join(gallery_path, ilustr_src)
                urlretrieve('%s/%s' % (remote_gallery_url, ilustr_src), ilustr_path)

    def load_abstract(self):
        abstract = self.wldocument(parse_dublincore=False).edoc.getroot().find('.//abstrakt')
        if abstract is not None:
            self.abstract = transform_abstrakt(abstract)
        else:
            self.abstract = ''

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
    def from_text_and_meta(cls, raw_file, book_info, overwrite=False, dont_build=None, search_index=True,
                           search_index_tags=True, remote_gallery_url=None, days=0):
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
                    raise Book.DoesNotExist(_('Book "%s" does not exist.') % part_url.slug)

        # Read book metadata
        book_slug = book_info.url.slug
        if re.search(r'[^a-z0-9-]', book_slug):
            raise ValueError('Invalid characters in slug')
        book, created = Book.objects.get_or_create(slug=book_slug)

        if created:
            book_shelves = []
            old_cover = None
            book.preview = bool(days)
            if book.preview:
                book.preview_until = date.today() + timedelta(days)
        else:
            if not overwrite:
                raise Book.AlreadyExists(_('Book %s already exists') % book_slug)
            # Save shelves for this book
            book_shelves = list(book.tags.filter(category='set'))
            old_cover = book.cover_info()

        # Save XML file
        book.xml_file.save('%s.xml' % book.slug, raw_file, save=False)
        if book.preview:
            book.xml_file.set_readable(False)

        book.language = book_info.language
        book.title = book_info.title
        if book_info.variant_of:
            book.common_slug = book_info.variant_of.slug
        else:
            book.common_slug = book.slug
        book.extra_info = book_info.to_dict()
        book.load_abstract()
        book.save()

        meta_tags = Tag.tags_from_info(book_info)

        for tag in meta_tags:
            if not tag.for_books:
                tag.for_books = True
                tag.save()

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
            if old_cover:
                notify_cover_changed.append(child)

        cls.repopulate_ancestors()
        tasks.update_counters.delay()

        if remote_gallery_url:
            book.download_pictures(remote_gallery_url)

        # No saves beyond this point.

        # Build cover.
        if 'cover' not in dont_build:
            book.cover.build_delay()
            book.cover_thumb.build_delay()
            book.cover_api_thumb.build_delay()
            book.simple_cover.build_delay()

        # Build HTML and ebooks.
        book.html_file.build_delay()
        if not children:
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

        book.save()  # update sort_key_author
        book.update_popularity()
        cls.published.send(sender=cls, instance=book)
        return book

    @classmethod
    @transaction.atomic
    def repopulate_ancestors(cls):
        """Fixes the ancestry cache."""
        # TODO: table names
        cursor = connection.cursor()
        if connection.vendor == 'postgres':
            cursor.execute("TRUNCATE catalogue_book_ancestor")
            cursor.execute("""
                WITH RECURSIVE ancestry AS (
                    SELECT book.id, book.parent_id
                    FROM catalogue_book AS book
                    WHERE book.parent_id IS NOT NULL
                    UNION
                    SELECT ancestor.id, book.parent_id
                    FROM ancestry AS ancestor, catalogue_book AS book
                    WHERE ancestor.parent_id = book.id
                        AND book.parent_id IS NOT NULL
                    )
                INSERT INTO catalogue_book_ancestor
                    (from_book_id, to_book_id)
                    SELECT id, parent_id
                    FROM ancestry
                    ORDER BY id;
                """)
        else:
            cursor.execute("DELETE FROM catalogue_book_ancestor")
            for b in cls.objects.exclude(parent=None):
                parent = b.parent
                while parent is not None:
                    b.ancestor.add(parent)
                    parent = parent.parent

    def clear_cache(self):
        clear_cached_renders(self.mini_box)
        clear_cached_renders(self.mini_box_nolink)

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

    def related_themes(self):
        return Tag.objects.usage_for_queryset(
            Fragment.objects.filter(models.Q(book=self) | models.Q(book__ancestor=self)),
            counts=True).filter(category='theme')

    def parent_cover_changed(self):
        """Called when parent book's cover image is changed."""
        if not self.cover_info(inherit=False):
            if 'cover' not in app_settings.DONT_BUILD:
                self.cover.build_delay()
                self.cover_thumb.build_delay()
                self.cover_api_thumb.build_delay()
                self.simple_cover.build_delay()
            for format_ in constants.EBOOK_FORMATS_WITH_COVERS:
                if format_ not in app_settings.DONT_BUILD:
                    getattr(self, '%s_file' % format_).build_delay()
            for child in self.children.all():
                child.parent_cover_changed()

    def other_versions(self):
        """Find other versions (i.e. in other languages) of the book."""
        return type(self).objects.filter(common_slug=self.common_slug).exclude(pk=self.pk)

    def parents(self):
        books = []
        parent = self.parent
        while parent is not None:
            books.insert(0, parent)
            parent = parent.parent
        return books

    def pretty_title(self, html_links=False):
        names = [(tag.name, tag.get_absolute_url()) for tag in self.authors().only('name', 'category', 'slug')]
        books = self.parents() + [self]
        names.extend([(b.title, b.get_absolute_url()) for b in books])

        if html_links:
            names = ['<a href="%s">%s</a>' % (tag[1], tag[0]) for tag in names]
        else:
            names = [tag[0] for tag in names]
        return ', '.join(names)

    def publisher(self):
        publisher = self.extra_info['publisher']
        if isinstance(publisher, str):
            return publisher
        elif isinstance(publisher, list):
            return ', '.join(publisher)

    @classmethod
    def tagged_top_level(cls, tags):
        """ Returns top-level books tagged with `tags`.

        It only returns those books which don't have ancestors which are
        also tagged with those tags.

        """
        objects = cls.tagged.with_all(tags)
        return objects.exclude(ancestor__in=objects)

    @classmethod
    def book_list(cls, book_filter=None):
        """Generates a hierarchical listing of all books.

        Books are optionally filtered with a test function.

        """

        books_by_parent = {}
        books = cls.objects.order_by('parent_number', 'sort_key').only('title', 'parent', 'slug', 'extra_info')
        if book_filter:
            books = books.filter(book_filter).distinct()

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
        books_by_author = OrderedDict()
        for tag in Tag.objects.filter(category='author').iterator():
            books_by_author[tag] = []

        for book in books_by_parent.get(None, ()):
            authors = list(book.authors().only('pk'))
            if authors:
                for author in authors:
                    books_by_author[author].append(book)
            else:
                orphans.append(book)

        return books_by_author, orphans, books_by_parent

    _audiences_pl = {
        "SP": (1, u"szkoła podstawowa"),
        "SP1": (1, u"szkoła podstawowa"),
        "SP2": (1, u"szkoła podstawowa"),
        "SP3": (1, u"szkoła podstawowa"),
        "P": (1, u"szkoła podstawowa"),
        "G": (2, u"gimnazjum"),
        "L": (3, u"liceum"),
        "LP": (3, u"liceum"),
    }

    def audiences_pl(self):
        audiences = self.extra_info.get('audiences', [])
        audiences = sorted(set([self._audiences_pl.get(a, (99, a)) for a in audiences]))
        return [a[1] for a in audiences]

    def stage_note(self):
        stage = self.extra_info.get('stage')
        if stage and stage < '0.4':
            return (_('This work needs modernisation'),
                    reverse('infopage', args=['wymagajace-uwspolczesnienia']))
        else:
            return None, None

    def choose_fragment(self):
        fragments = self.fragments.order_by()
        fragments_count = fragments.count()
        if not fragments_count and self.children.exists():
            fragments = Fragment.objects.filter(book__ancestor=self).order_by()
            fragments_count = fragments.count()
        if fragments_count:
            return fragments[randint(0, fragments_count - 1)]
        elif self.parent:
            return self.parent.choose_fragment()
        else:
            return None

    def fragment_data(self):
        fragment = self.choose_fragment()
        if fragment:
            return {
                'title': fragment.book.pretty_title(),
                'html': re.sub('</?blockquote[^>]*>', '', fragment.get_short_text()),
            }
        else:
            return None

    def update_popularity(self):
        count = self.tags.filter(category='set').values('user').order_by('user').distinct().count()
        try:
            pop = self.popularity
            pop.count = count
            pop.save()
        except BookPopularity.DoesNotExist:
            BookPopularity.objects.create(book=self, count=count)

    def ridero_link(self):
        return 'https://ridero.eu/%s/books/wl_%s/' % (get_language(), self.slug.replace('-', '_'))

    def like(self, user):
        from social.utils import likes, get_set, set_sets
        if not likes(user, self):
            tag = get_set(user, '')
            set_sets(user, self, [tag])

    def unlike(self, user):
        from social.utils import likes, set_sets
        if likes(user, self):
            set_sets(user, self, [])

    def full_sort_key(self):
        return self.SORT_KEY_SEP.join((self.sort_key_author, self.sort_key, str(self.id)))

    def cover_color(self):
        return WLCover.epoch_colors.get(self.extra_info.get('epoch'), '#000000')

    @cached_render('catalogue/book_mini_box.html')
    def mini_box(self):
        return {
            'book': self
        }

    @cached_render('catalogue/book_mini_box.html')
    def mini_box_nolink(self):
        return {
            'book': self,
            'no_link': True,
        }

def add_file_fields():
    for format_ in Book.formats:
        field_name = "%s_file" % format_
        # This weird globals() assignment makes Django migrations comfortable.
        _upload_to = _ebook_upload_to('book/%s/%%s.%s' % (format_, format_))
        _upload_to.__name__ = '_%s_upload_to' % format_
        globals()[_upload_to.__name__] = _upload_to

        EbookField(
            format_, _("%s file" % format_.upper()),
            upload_to=_upload_to,
            storage=bofh_storage,
            max_length=255,
            blank=True,
            default=''
        ).contribute_to_class(Book, field_name)


add_file_fields()


class BookPopularity(models.Model):
    book = models.OneToOneField(Book, models.CASCADE, related_name='popularity')
    count = models.IntegerField(default=0, db_index=True)
