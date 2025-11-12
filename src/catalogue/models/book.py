# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from collections import OrderedDict
import json
from datetime import date, timedelta
from random import randint
import os.path
import re
from slugify import slugify
from sortify import sortify
from urllib.request import urlretrieve
from django.apps import apps
from django.conf import settings
from django.db import connection, models, transaction
import django.dispatch
from django.contrib.contenttypes.fields import GenericRelation
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _, get_language
from fnpdjango.storage import BofhFileSystemStorage
from lxml import html
from librarian.cover import WLCover
from librarian.html import transform_abstrakt
from librarian.builders import builders
from newtagging import managers
from catalogue import constants
from catalogue import fields
from catalogue.models import Tag, Fragment, BookMedia
from catalogue.utils import create_zip, gallery_url, gallery_path, split_tags, get_random_hash
from catalogue.models.tag import prefetched_relations
from catalogue import app_settings
from wolnelektury.utils import makedirs, cached_render, clear_cached_renders

bofh_storage = BofhFileSystemStorage()


class Book(models.Model):
    """Represents a book imported from WL-XML."""
    title = models.CharField('tytuł', max_length=32767)
    sort_key = models.CharField('klucz sortowania', max_length=120, db_index=True, editable=False)
    sort_key_author = models.CharField(
        'klucz sortowania wg autora', max_length=120, db_index=True, editable=False, default='')
    slug = models.SlugField('slug', max_length=120, db_index=True, unique=True)
    common_slug = models.SlugField('wspólny slug', max_length=120, db_index=True)
    language = models.CharField('kod języka', max_length=3, db_index=True, default=app_settings.DEFAULT_LANGUAGE)
    description = models.TextField('opis', blank=True)
    license = models.CharField('licencja', max_length=255, blank=True, db_index=True)
    abstract = models.TextField('abstrakt', blank=True)
    toc = models.TextField('spis treści', blank=True)
    created_at = models.DateTimeField('data utworzenia', auto_now_add=True, db_index=True)
    changed_at = models.DateTimeField('data motyfikacji', auto_now=True, db_index=True)
    parent_number = models.IntegerField('numer w ramach rodzica', default=0)
    extra_info = models.TextField('dodatkowe informacje', default='{}')
    gazeta_link = models.CharField(blank=True, max_length=240)
    wiki_link = models.CharField(blank=True, max_length=240)
    print_on_demand = models.BooleanField('druk na żądanie', default=False)
    recommended = models.BooleanField('polecane', default=False)
    audio_length = models.CharField('długość audio', blank=True, max_length=8)
    preview = models.BooleanField('prapremiera', default=False)
    preview_until = models.DateField('prapremiera do', blank=True, null=True)
    preview_key = models.CharField(max_length=32, blank=True, null=True)
    findable = models.BooleanField('wyszukiwalna', default=True, db_index=True)

    # files generated during publication
    xml_file = fields.XmlField(storage=bofh_storage, with_etag=False)
    html_file = fields.HtmlField(storage=bofh_storage)
    html_nonotes_file = fields.HtmlNonotesField(storage=bofh_storage)
    fb2_file = fields.Fb2Field(storage=bofh_storage)
    txt_file = fields.TxtField(storage=bofh_storage)
    epub_file = fields.EpubField(storage=bofh_storage)
    mobi_file = fields.MobiField(storage=bofh_storage)
    pdf_file = fields.PdfField(storage=bofh_storage)

    cover = fields.CoverField('okładka', storage=bofh_storage)
    # Cleaner version of cover for thumbs
    cover_clean = fields.CoverCleanField('czysta okładka')
    cover_thumb = fields.CoverThumbField('miniatura okładki')
    cover_api_thumb = fields.CoverApiThumbField(
        'mniaturka okładki dla aplikacji')
    simple_cover = fields.SimpleCoverField('okładka dla aplikacji')
    cover_ebookpoint = fields.CoverEbookpointField(
        'okładka dla Ebookpoint')

    ebook_formats = constants.EBOOK_FORMATS
    formats = ebook_formats + ['html', 'xml', 'html_nonotes']

    parent = models.ForeignKey('self', models.CASCADE, blank=True, null=True, related_name='children')
    ancestor = models.ManyToManyField('self', blank=True, editable=False, related_name='descendant', symmetrical=False)

    cached_author = models.CharField(blank=True, max_length=240, db_index=True)
    has_audience = models.BooleanField(default=False)

    objects = models.Manager()
    tagged = managers.ModelTaggedItemManager(Tag)
    tags = managers.TagDescriptor(Tag)
    tag_relations = GenericRelation(Tag.intermediary_table_model, related_query_name='tagged_book')
    translators = models.ManyToManyField(Tag, blank=True)
    narrators = models.ManyToManyField(Tag, blank=True, related_name='narrated')
    has_audio = models.BooleanField(default=False)

    html_built = django.dispatch.Signal()
    published = django.dispatch.Signal()

    SORT_KEY_SEP = '$'

    is_book = True

    class AlreadyExists(Exception):
        pass

    class Meta:
        ordering = ('sort_key_author', 'sort_key')
        verbose_name = 'książka'
        verbose_name_plural = 'książki'
        app_label = 'catalogue'

    def __str__(self):
        return self.title

    def get_extra_info_json(self):
        return json.loads(self.extra_info or '{}')

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
        translators = self.get_extra_info_json().get('translators')
        if not translators:
            return None
        if len(translators) > 3:
            translators = translators[:2]
            others = ' i inni'
        else:
            others = ''
        return ', '.join('\xa0'.join(reversed(translator.split(', ', 1))) for translator in translators) + others

    def cover_source(self):
        return self.get_extra_info_json().get('cover_source', self.parent.cover_source() if self.parent else '')

    @property
    def isbn_pdf(self):
        return self.get_extra_info_json().get('isbn_pdf')

    @property
    def isbn_epub(self):
        return self.get_extra_info_json().get('isbn_epub')

    @property
    def isbn_mobi(self):
        return self.get_extra_info_json().get('isbn_mobi')

    def is_accessible_to(self, user):
        if not self.preview:
            return True
        if not user.is_authenticated:
            return False
        Membership = apps.get_model('club', 'Membership')
        if Membership.is_active_for(user):
            return True
        Funding = apps.get_model('funding', 'Funding')
        if Funding.objects.filter(user=user, offer__book=self):
            return True
        return False

    def save(self, force_insert=False, force_update=False, **kwargs):
        from sortify import sortify

        self.sort_key = sortify(self.title)[:120]
        self.title = str(self.title)  # ???

        try:
            author = self.authors().first().sort_key
        except AttributeError:
            author = ''
        self.sort_key_author = author

        self.cached_author = self.tag_unicode('author')
        self.has_audience = 'audience' in self.get_extra_info_json()

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

    def get_first_text(self):
        if self.html_file:
            return self
        child = self.children.all().order_by('parent_number').first()
        if child is not None:
            return child.get_first_text()

    def get_last_text(self):
        if self.html_file:
            return self
        child = self.children.all().order_by('parent_number').last()
        if child is not None:
            return child.get_last_text()

    def get_prev_text(self):
        if not self.parent:
            return None
        sibling = self.parent.children.filter(parent_number__lt=self.parent_number).order_by('-parent_number').first()
        if sibling is not None:
            return sibling.get_last_text()

        if self.parent.html_file:
            return self.parent

        return self.parent.get_prev_text()

    def get_next_text(self, inside=True):
        if inside:
            child = self.children.order_by('parent_number').first()
            if child is not None:
                return child.get_first_text()

        if not self.parent:
            return None
        sibling = self.parent.children.filter(parent_number__gt=self.parent_number).order_by('parent_number').first()
        if sibling is not None:
            return sibling.get_first_text()
        return self.parent.get_next_text(inside=False)

    def get_siblings(self):
        if not self.parent:
            return []
        return self.parent.children.all().order_by('parent_number')

    def get_children(self):
        return self.children.all().order_by('parent_number')

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
        """
        >>> Book.format_audio_length(1)
        '0:01'
        >>> Book.format_audio_length(3661)
        '1:01:01'
        """
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

    def get_time(self):
        return round(self.xml_file.size / 1000 * 40)
    
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

    def get_audio_epub(self):
        return self.get_media("audio.epub")

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

    def html_nonotes_url(self):
        return self.media_url('html_nonotes')

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
    has_description.short_description = 'opis'
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

    def has_sync_file(self):
        return settings.FEATURE_SYNCHRO and self.has_media("sync")

    def build_sync_file(self):
        from lxml import html
        from django.core.files.base import ContentFile
        with self.html_file.open('rb') as f:
            h = html.fragment_fromstring(f.read().decode('utf-8'))

        durations = [
            m['mp3'].duration
            for m in self.get_audiobooks()[0]
        ]
        if settings.MOCK_DURATIONS:
            durations = settings.MOCK_DURATIONS

        sync = []
        ts = None
        sid = 1
        dirty = False
        for elem in h.iter():
            if elem.get('data-audio-ts'):
                part, ts = int(elem.get('data-audio-part')), float(elem.get('data-audio-ts'))
                ts = str(round(sum(durations[:part - 1]) + ts, 3))
                # check if inside verse
                p = elem.getparent()
                while p is not None:
                    # Workaround for missing ids.
                    if 'verse' in p.get('class', ''):
                        if not p.get('id'):
                            p.set('id', f'syn{sid}')
                            dirty = True
                            sid += 1
                        sync.append((ts, p.get('id')))
                        ts = None
                        break
                    p = p.getparent()
            elif ts:
                cls = elem.get('class', '')
                # Workaround for missing ids.
                if 'paragraph' in cls or 'verse' in cls or elem.tag in ('h1', 'h2', 'h3', 'h4'):
                    if not elem.get('id'):
                        elem.set('id', f'syn{sid}')
                        dirty = True
                        sid += 1
                    sync.append((ts, elem.get('id')))
                    ts = None
        if dirty:
            htext = html.tostring(h, encoding='utf-8')
            with open(self.html_file.path, 'wb') as f:
                f.write(htext)
        try:
            bm = self.media.get(type='sync')
        except:
            bm = BookMedia(book=self, type='sync')
        sync = (
            '27\n' + '\n'.join(
                f'{s[0]}\t{sync[i+1][0]}\t{s[1]}' for i, s in enumerate(sync[:-1])
            )).encode('latin1')
        bm.file.save(
            None, ContentFile(sync)
            )

    
    def get_sync(self):
        if not self.has_sync_file():
            return '[]'
        with self.get_media('sync').first().file.open('r') as f:
            sync = f.read().split('\n')
        offset = float(sync[0])
        items = []
        for line in sync[1:]:
            if not line:
                continue
            start, end, elid = line.split()
            items.append([elid, float(start) + offset])
        return json.dumps(items)
    
    def has_audio_epub_file(self):
        return self.has_media("audio.epub")

    @property
    def media_daisy(self):
        return self.get_media('daisy')

    @property
    def media_audio_epub(self):
        return self.get_media('audio.epub')

    def get_audiobooks(self, with_children=False, processing=False):
        ogg_files = {}
        for m in self.media.filter(type='ogg').order_by().iterator():
            ogg_files[m.name] = m

        audiobooks = []
        projects = set()
        total_duration = 0
        for mp3 in self.media.filter(type='mp3').iterator():
            # ogg files are always from the same project
            meta = mp3.get_extra_info_json()
            project = meta.get('project')
            if not project:
                # temporary fallback
                project = 'CzytamySłuchając'

            projects.add((project, meta.get('funded_by', '')))
            total_duration += mp3.duration or 0

            media = {'mp3': mp3}

            ogg = ogg_files.get(mp3.name)
            if ogg:
                media['ogg'] = ogg
            audiobooks.append(media)

        if with_children:
            for child in self.get_children():
                ch_audiobooks, ch_projects, ch_duration = child.get_audiobooks(
                    with_children=True, processing=True)
                audiobooks.append({'part': child})
                audiobooks += ch_audiobooks
                projects.update(ch_projects)
                total_duration += ch_duration

        if not processing:
            projects = sorted(projects)
            total_duration = '%d:%02d' % (
                total_duration // 60,
                total_duration % 60
            )

        return audiobooks, projects, total_duration

    def get_audiobooks_with_children(self):
        return self.get_audiobooks(with_children=True)
    
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

    def wldocument2(self):
        from catalogue.import_utils import ORMDocProvider
        from librarian.document import WLDocument
        doc = WLDocument(
            self.xml_file.path,
            provider=ORMDocProvider(self)
        )
        doc.meta.update(self.cover_info())
        return doc


    @staticmethod
    def zip_format(format_):
        def pretty_file_name(book):
            return "%s/%s.%s" % (
                book.get_extra_info_json()['author'],
                book.slug,
                format_)

        field_name = "%s_file" % format_
        field = getattr(Book, field_name)
        books = Book.objects.filter(parent=None).exclude(**{field_name: ""}).exclude(preview=True).exclude(findable=False)
        paths = [(pretty_file_name(b), getattr(b, field_name).path) for b in books.iterator()]
        return create_zip(paths, field.ZIP)

    def zip_audiobooks(self, format_):
        bm = BookMedia.objects.filter(book=self, type=format_)
        paths = map(lambda bm: (bm.get_nice_filename(), bm.file.path), bm)
        licenses = set()
        for m in bm:
            license = constants.LICENSES.get(
                m.get_extra_info_json().get('license'), {}
            ).get('locative')
            if license:
                licenses.add(license)
        readme = render_to_string('catalogue/audiobook_zip_readme.txt', {
            'licenses': licenses,
            'meta': self.wldocument2().meta,
        })
        return create_zip(paths, "%s_%s" % (self.slug, format_), {'informacje.txt': readme})

    def search_index(self, index=None):
        if not self.findable:
            return
        from search.index import Index
        Index.index_book(self)

    # will make problems in conjunction with paid previews
    def download_pictures(self, remote_gallery_url):
        # This is only needed for legacy relative image paths.
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
                if '/' in ilustr_src:
                    continue
                ilustr_path = os.path.join(gallery_path, ilustr_src)
                urlretrieve('%s/%s' % (remote_gallery_url, ilustr_src), ilustr_path)

    def load_abstract(self):
        abstract = self.wldocument(parse_dublincore=False).edoc.getroot().find('.//abstrakt')
        if abstract is not None:
            self.abstract = transform_abstrakt(abstract)
        else:
            self.abstract = ''

    def load_toc(self):
        self.toc = ''
        if self.html_file:
            parser = html.HTMLParser(encoding='utf-8')
            tree = html.parse(self.html_file.path, parser=parser)
            toc = tree.find('//div[@id="toc"]/ol')
            if toc is None or not len(toc):
                return
            html_link = reverse('book_text', args=[self.slug])
            for a in toc.findall('.//a'):
                a.attrib['href'] = html_link + a.attrib['href']
            self.toc = html.tostring(toc, encoding='unicode')
            # div#toc

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
                           remote_gallery_url=None, days=0, findable=True, logo=None, logo_mono=None, logo_alt=None):
        from catalogue import tasks

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
                    raise Book.DoesNotExist('Książka "%s" nie istnieje.' % part_url.slug)

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
                raise Book.AlreadyExists('Książka %s już istnieje' % book_slug)
            # Save shelves for this book
            book_shelves = list(book.tags.filter(category='set'))
            old_cover = book.cover_info()

        # Save XML file
        book.xml_file.save('%s.xml' % book.slug, raw_file, save=False)
        if book.preview:
            book.xml_file.set_readable(False)

        book.findable = findable
        book.language = book_info.language
        book.title = book_info.title
        book.license = book_info.license or ''
        if book_info.variant_of:
            book.common_slug = book_info.variant_of.slug
        else:
            book.common_slug = book.slug
        extra = book_info.to_dict()
        if logo:
            extra['logo'] = logo
        if logo_mono:
            extra['logo_mono'] = logo_mono
        if logo_alt:
            extra['logo_alt'] = logo_alt
        book.extra_info = json.dumps(extra)
        book.load_abstract()
        book.load_toc()
        book.save()

        meta_tags = Tag.tags_from_info(book_info)

        just_tags = [t for (t, rel) in meta_tags if not rel]
        book.tags = set(just_tags + book_shelves)
        book.save()  # update sort_key_author

        book.translators.set([t for (t, rel) in meta_tags if rel == 'translator'])

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
            book.cover_clean.build_delay()
            book.cover_thumb.build_delay()
            book.cover_api_thumb.build_delay()
            book.simple_cover.build_delay()
            book.cover_ebookpoint.build_delay()

        # Build HTML and ebooks.
        book.html_file.build_delay()
        if not children:
            for format_ in constants.EBOOK_FORMATS_WITHOUT_CHILDREN:
                if format_ not in dont_build:
                    getattr(book, '%s_file' % format_).build_delay()
        for format_ in constants.EBOOK_FORMATS_WITH_CHILDREN:
            if format_ not in dont_build:
                getattr(book, '%s_file' % format_).build_delay()
        book.html_nonotes_file.build_delay()

        if not settings.NO_SEARCH_INDEX and search_index and findable:
            tasks.index_book.delay(book.id)

        for child in notify_cover_changed:
            child.parent_cover_changed()

        book.update_popularity()
        tasks.update_references.delay(book.id)

        cls.published.send(sender=cls, instance=book)
        return book

    def update_references(self):
        Entity = apps.get_model('references', 'Entity')
        doc = self.wldocument2()
        doc._compat_assign_section_ids()
        doc._compat_assign_ordered_ids()
        refs = {}
        for ref_elem in doc.references():
            uri = ref_elem.attrib.get('href', '')
            if not uri:
                continue
            if uri in refs:
                ref = refs[uri]
            else:
                entity, entity_created = Entity.objects.get_or_create(uri=uri)
                if entity_created:
                    try:
                        entity.populate()
                    except:
                        pass
                    else:
                        entity.save()
                ref, ref_created = entity.reference_set.get_or_create(book=self)
                refs[uri] = ref
                if not ref_created:
                    ref.occurence_set.all().delete()
            sec = ref_elem.get_link()
            m = re.match(r'sec(\d+)', sec)
            assert m is not None
            sec = int(m.group(1))
            snippet = ref_elem.get_snippet()
            b = builders['html-snippet']()
            for s in snippet:
                s.html_build(b)
            html = b.output().get_bytes().decode('utf-8')

            ref.occurence_set.create(
                section=sec,
                html=html
            )
        self.reference_set.exclude(entity__uri__in=refs).delete()

    @property
    def references(self):
        return self.reference_set.all().select_related('entity')

    def update_has_audio(self):
        self.has_audio = False
        if self.media.filter(type='mp3').exists():
            self.has_audio = True
        if self.descendant.filter(has_audio=True).exists():
            self.has_audio = True
        self.save(update_fields=['has_audio'])
        if self.parent is not None:
            self.parent.update_has_audio()

    def update_narrators(self):
        narrator_names = set()
        for bm in self.media.filter(type='mp3'):
            narrator_names.update(set(
                a.strip() for a in re.split(r',|\si\s', bm.artist)
            ))
        narrators = []

        for name in narrator_names:
            if not name: continue
            slug = slugify(name)
            try:
                t = Tag.objects.get(category='author', slug=slug)
            except Tag.DoesNotExist:
                sort_key = sortify(
                    ' '.join(name.rsplit(' ', 1)[::-1]).lower()
                )
                t = Tag.objects.create(
                    category='author',
                    name_pl=name,
                    slug=slug,
                    sort_key=sort_key,
                )
            narrators.append(t)
        self.narrators.set(narrators)

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

    @property
    def ancestors(self):
        if self.parent:
            for anc in self.parent.ancestors:
                yield anc
            yield self.parent
        else:
            return []

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
            val = self.get_extra_info_json().get(field)
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
            counts=True).filter(category='theme').order_by('-count')

    def parent_cover_changed(self):
        """Called when parent book's cover image is changed."""
        if not self.cover_info(inherit=False):
            if 'cover' not in app_settings.DONT_BUILD:
                self.cover.build_delay()
                self.cover_clean.build_delay()
                self.cover_thumb.build_delay()
                self.cover_api_thumb.build_delay()
                self.simple_cover.build_delay()
                self.cover_ebookpoint.build_delay()
            for format_ in constants.EBOOK_FORMATS_WITH_COVERS:
                if format_ not in app_settings.DONT_BUILD:
                    getattr(self, '%s_file' % format_).build_delay()
            for child in self.children.all():
                child.parent_cover_changed()

    def other_versions(self):
        """Find other versions (i.e. in other languages) of the book."""
        return type(self).objects.filter(common_slug=self.common_slug, findable=True).exclude(pk=self.pk)

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
        publisher = self.get_extra_info_json()['publisher']
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
        return objects.filter(findable=True).exclude(ancestor__in=objects)

    @classmethod
    def book_list(cls, book_filter=None):
        """Generates a hierarchical listing of all books.

        Books are optionally filtered with a test function.

        """

        books_by_parent = {}
        books = cls.objects.filter(findable=True).order_by('parent_number', 'sort_key').only('title', 'parent', 'slug', 'extra_info')
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
        "SP": (1, "szkoła podstawowa"),
        "SP1": (1, "szkoła podstawowa"),
        "SP2": (1, "szkoła podstawowa"),
        "SP3": (1, "szkoła podstawowa"),
        "P": (1, "szkoła podstawowa"),
        "G": (2, "gimnazjum"),
        "L": (3, "liceum"),
        "LP": (3, "liceum"),
    }

    def audiences_pl(self):
        audiences = self.get_extra_info_json().get('audiences', [])
        audiences = sorted(set([self._audiences_pl.get(a, (99, a)) for a in audiences]))
        return [a[1] for a in audiences]

    def stage_note(self):
        stage = self.get_extra_info_json().get('stage')
        if stage and stage < '0.4':
            return (_('Ten utwór wymaga uwspółcześnienia'),
                    reverse('infopage', args=['wymagajace-uwspolczesnienia']))
        else:
            return None, None

    def choose_fragments(self, number):
        fragments = self.fragments.order_by()
        fragments_count = fragments.count()
        if not fragments_count and self.children.exists():
            fragments = Fragment.objects.filter(book__ancestor=self).order_by()
            fragments_count = fragments.count()
        if fragments_count:
            if fragments_count > number:
                offset = randint(0, fragments_count - number)
            else:
                offset = 0
            return fragments[offset : offset + number]
        elif self.parent:
            return self.parent.choose_fragments(number)
        else:
            return []

    def choose_fragment(self):
        fragments = self.choose_fragments(1)
        if fragments:
            return fragments[0]
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
        count = self.userlistitem_set.values('list__user').order_by('list__user').distinct().count()
        try:
            pop = self.popularity
            pop.count = count
            pop.save()
        except BookPopularity.DoesNotExist:
            BookPopularity.objects.create(book=self, count=count)

    def ridero_link(self):
        return 'https://ridero.eu/%s/books/wl_%s/' % (get_language(), self.slug.replace('-', '_'))

    def full_sort_key(self):
        return self.SORT_KEY_SEP.join((self.sort_key_author, self.sort_key, str(self.id)))

    def cover_color(self):
        return WLCover.epoch_colors.get(self.get_extra_info_json().get('epoch'), '#000000')

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


class BookPopularity(models.Model):
    book = models.OneToOneField(Book, models.CASCADE, related_name='popularity')
    count = models.IntegerField(default=0, db_index=True)
