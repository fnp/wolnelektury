# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
import io
import os
import pkg_resources
import random
import time
from urllib.request import urlopen
from django.apps import apps
from django.conf import settings
from django.core.files import File
from django.db import models
from django.db.models.fields.files import FieldFile
from django.utils.deconstruct import deconstructible
from librarian.cover import make_cover
from catalogue.constants import LANGUAGES_3TO2
from catalogue.utils import absolute_url, remove_zip, truncate_html_words, gallery_path, gallery_url
from waiter.utils import clear_cache

ETAG_SCHEDULED_SUFFIX = '-scheduled'
EBOOK_BUILD_PRIORITY = 0
EBOOK_REBUILD_PRIORITY = 9


@deconstructible
class UploadToPath(object):
    def __init__(self, path):
        self.path = path

    def __call__(self, instance, filename):
        return self.path % instance.slug

    def __eq__(self, other):
        return isinstance(other, type(self)) and other.path == self.path


def get_make_cover(book):
    extra = book.get_extra_info_json()
    cover_logo = extra.get('logo_mono', extra.get('logo'))
    if cover_logo:
        while True:
            try:
                cover_logo = io.BytesIO(urlopen(cover_logo, timeout=3).read())
            except:
                time.sleep(2)
            else:
                break
    
    def mc(*args, **kwargs):
        if cover_logo:
            kwargs['cover_logo'] = cover_logo
        return make_cover(*args, **kwargs)
    return mc
    

class EbookFieldFile(FieldFile):
    """Represents contents of an ebook file field."""

    def build(self):
        """Build the ebook immediately."""
        etag = self.field.get_current_etag()
        self.field.build(self)
        self.update_etag(etag)
        self.instance.clear_cache()

    def build_delay(self, priority=EBOOK_BUILD_PRIORITY):
        """Builds the ebook in a delayed task."""
        from .tasks import build_field

        self.update_etag(
            "".join([self.field.get_current_etag(), ETAG_SCHEDULED_SUFFIX])
        )
        return build_field.apply_async(
            [self.instance.pk, self.field.attname],
            priority=priority
        )

    def set_readable(self, readable):
        import os
        permissions = 0o644 if readable else 0o600
        os.chmod(self.path, permissions)

    def update_etag(self, etag):
        setattr(self.instance, self.field.etag_field_name, etag)
        if self.instance.pk:
            self.instance.save(update_fields=[self.field.etag_field_name])


class EbookField(models.FileField):
    """Represents an ebook file field, attachable to a model."""
    attr_class = EbookFieldFile
    ext = None
    for_parents = True
    librarian2_api = False
    ZIP = None

    def __init__(self, verbose_name=None, with_etag=True, etag_field_name=None, **kwargs):
        kwargs.setdefault('verbose_name', verbose_name)
        self.with_etag = with_etag
        self.etag_field_name = etag_field_name
        kwargs.setdefault('max_length', 255)
        kwargs.setdefault('blank', True)
        kwargs.setdefault('default', '')
        kwargs.setdefault('upload_to', self.get_upload_to(self.ext))

        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs.get('max_length') == 255:
            del kwargs['max_length']
        if kwargs.get('blank') is True:
            del kwargs['blank']
        if kwargs.get('default') == '':
            del kwargs['default']
        if self.get_upload_to(self.ext) == kwargs.get('upload_to'):
            del kwargs['upload_to']
        # with_etag creates a second field, which then deconstructs to manage
        # its own migrations. So for migrations, etag_field_name is explicitly
        # set to avoid double creation of the etag field.
        if self.with_etag:
            kwargs['etag_field_name'] = self.etag_field_name
        else:
            kwargs['with_etag'] = self.with_etag

        return name, path, args, kwargs

    @classmethod
    def get_upload_to(cls, directory):
        directory = getattr(cls, 'directory', cls.ext)
        upload_template = f'book/{directory}/%s.{cls.ext}'
        return UploadToPath(upload_template)

    def contribute_to_class(self, cls, name):
        super(EbookField, self).contribute_to_class(cls, name)

        if self.with_etag and not self.etag_field_name:
            self.etag_field_name = f'{name}_etag'
            self.etag_field = models.CharField(max_length=255, editable=False, default='', db_index=True)
            self.etag_field.contribute_to_class(cls, f'{name}_etag')

        def has(model_instance):
            return bool(getattr(model_instance, self.attname, None))
        has.__doc__ = None
        has.__name__ = str("has_%s" % self.attname)
        has.short_description = self.name
        has.boolean = True

        setattr(cls, 'has_%s' % self.attname, has)

    def get_current_etag(self):
        MediaInsertSet = apps.get_model('annoy', 'MediaInsertSet')
        librarian_version = pkg_resources.get_distribution("librarian").version
        etag = librarian_version
        mis = MediaInsertSet.get_for_format(self.ext)
        if mis is not None:
            etag += '_' + mis.etag
        return etag

    def find_stale(self, limit):
        """Find some books where this format is stale."""
        # If there is not ETag field, bail. That's true for xml file field.
        if not self.with_etag:
            return []

        etag = self.get_current_etag()

        queryset = self.model.objects.all()
        if not self.for_parents:
            queryset = queryset.filter(children=None)

        queryset = queryset.exclude(**{
            f'{self.etag_field_name}__in': [
                etag, f'{etag}{ETAG_SCHEDULED_SUFFIX}'
           ]
        })

        queryset = queryset.order_by('?')[:limit]
        return queryset

    @classmethod
    def find_all_stale(cls, model, limit):
        """Schedules all stale ebooks of all formats to rebuild."""
        found = []
        for field in model._meta.fields:
            if isinstance(field, cls):
                for instance in field.find_stale(limit):
                    found.append((
                        field.name,
                        instance
                    ))
        random.shuffle(found)
        found = found[:limit]
        return found

    @staticmethod
    def transform(wldoc, book):
        """Transforms an librarian.WLDocument into an librarian.OutputFile.
        """
        raise NotImplemented()

    def set_file_permissions(self, fieldfile):
        if fieldfile.instance.preview:
            fieldfile.set_readable(False)

    def build(self, fieldfile):
        book = fieldfile.instance
        out = self.transform(
            book.wldocument2() if self.librarian2_api else book.wldocument(),
            book,
        )
        with open(out.get_filename(), 'rb') as f:
            fieldfile.save(None, File(f), save=False)
        self.set_file_permissions(fieldfile)
        if book.pk is not None:
            book.save(update_fields=[self.attname])
        if self.ZIP:
            remove_zip(self.ZIP)


class XmlField(EbookField):
    ext = 'xml'

    def build(self, fieldfile):
        pass


class TxtField(EbookField):
    ext = 'txt'
    for_parents = False

    @staticmethod
    def transform(wldoc, book):
        return wldoc.as_text()


class Fb2Field(EbookField):
    ext = 'fb2'
    for_parents = False
    ZIP = 'wolnelektury_pl_fb2'

    @staticmethod
    def transform(wldoc, book):
        return wldoc.as_fb2()


class PdfField(EbookField):
    ext = 'pdf'
    ZIP = 'wolnelektury_pl_pdf'

    @staticmethod
    def transform(wldoc, book):
        MediaInsertSet = apps.get_model('annoy', 'MediaInsertSet')
        return wldoc.as_pdf(
            morefloats=settings.LIBRARIAN_PDF_MOREFLOATS,
            cover=get_make_cover(book),
            base_url=absolute_url(gallery_url(wldoc.book_info.url.slug)), customizations=['notoc'],
            fundraising=MediaInsertSet.get_texts_for('pdf'),
        )

    def build(self, fieldfile):
        super().build(fieldfile)
        clear_cache(fieldfile.instance.slug)


class EpubField(EbookField):
    ext = 'epub'
    librarian2_api = True
    ZIP = 'wolnelektury_pl_epub'

    @staticmethod
    def transform(wldoc, book):
        from librarian.builders import EpubBuilder
        MediaInsertSet = apps.get_model('annoy', 'MediaInsertSet')
        return EpubBuilder(
                base_url='file://' + os.path.abspath(gallery_path(wldoc.meta.url.slug)) + '/',
                fundraising=MediaInsertSet.get_texts_for('epub'),
                cover=get_make_cover(book),
            ).build(wldoc)


class MobiField(EbookField):
    ext = 'mobi'
    librarian2_api = True
    ZIP = 'wolnelektury_pl_mobi'

    @staticmethod
    def transform(wldoc, book):
        from librarian.builders import MobiBuilder
        MediaInsertSet = apps.get_model('annoy', 'MediaInsertSet')
        return MobiBuilder(
                base_url='file://' + os.path.abspath(gallery_path(wldoc.meta.url.slug)) + '/',
                fundraising=MediaInsertSet.get_texts_for('mobi'),
                cover=get_make_cover(book),
            ).build(wldoc)


class HtmlField(EbookField):
    ext = 'html'
    for_parents = False

    def build(self, fieldfile):
        from django.core.files.base import ContentFile
        from slugify import slugify
        from sortify import sortify
        from librarian import html
        from catalogue.models import Fragment, Tag

        book = fieldfile.instance

        html_output = self.transform(book.wldocument(parse_dublincore=False), book)

        # Delete old fragments, create from scratch if necessary.
        book.fragments.all().delete()

        if html_output:
            meta_tags = list(book.tags.filter(
                category__in=('author', 'epoch', 'genre', 'kind')))

            lang = book.language
            lang = LANGUAGES_3TO2.get(lang, lang)
            if lang not in [ln[0] for ln in settings.LANGUAGES]:
                lang = None

            fieldfile.save(None, ContentFile(html_output.get_bytes()), save=False)
            self.set_file_permissions(fieldfile)
            type(book).objects.filter(pk=book.pk).update(**{
                fieldfile.field.attname: fieldfile
            })

            # Extract fragments
            closed_fragments, open_fragments = html.extract_fragments(fieldfile.path)
            for fragment in closed_fragments.values():
                try:
                    theme_names = [s.strip() for s in fragment.themes.split(',')]
                except AttributeError:
                    continue
                themes = []
                for theme_name in theme_names:
                    if not theme_name:
                        continue
                    if lang == settings.LANGUAGE_CODE:
                        # Allow creating themes if book in default language.
                        tag, created = Tag.objects.get_or_create(
                            slug=slugify(theme_name),
                            category='theme'
                        )
                        if created:
                            tag.name = theme_name
                            setattr(tag, "name_%s" % lang, theme_name)
                            tag.sort_key = sortify(theme_name.lower())
                            tag.for_books = True
                            tag.save()
                        themes.append(tag)
                    elif lang is not None:
                        # Don't create unknown themes in non-default languages.
                        try:
                            tag = Tag.objects.get(
                                category='theme',
                                **{"name_%s" % lang: theme_name}
                            )
                        except Tag.DoesNotExist:
                            pass
                        else:
                            themes.append(tag)
                if not themes:
                    continue

                text = fragment.to_string()
                short_text = truncate_html_words(text, 15)
                if text == short_text:
                    short_text = ''
                new_fragment = Fragment.objects.create(
                    anchor=fragment.id,
                    book=book,
                    text=text,
                    short_text=short_text
                )

                new_fragment.save()
                new_fragment.tags = set(meta_tags + themes)
                for theme in themes:
                    if not theme.for_books:
                        theme.for_books = True
                        theme.save()
            book.html_built.send(sender=type(self), instance=book)
            return True
        return False

    @staticmethod
    def transform(wldoc, book):
        # ugly, but we can't use wldoc.book_info here
        from librarian import DCNS
        url_elem = wldoc.edoc.getroot().find('.//' + DCNS('identifier.url'))
        if url_elem is None:
            gal_url = ''
            gal_path = ''
        else:
            slug = url_elem.text.rstrip('/').rsplit('/', 1)[1]
            gal_url = gallery_url(slug=slug)
            gal_path = gallery_path(slug=slug)
        return wldoc.as_html(gallery_path=gal_path, gallery_url=gal_url, base_url=absolute_url(gal_url))


class CoverField(EbookField):
    ext = 'jpg'
    directory = 'cover'

    @staticmethod
    def transform(wldoc, book):
        return get_make_cover(book)(wldoc.book_info, width=360).output_file()

    def set_file_permissions(self, fieldfile):
        pass


class CoverCleanField(CoverField):
    directory = 'cover_clean'

    @staticmethod
    def transform(wldoc, book):
        return get_make_cover(book)(wldoc.book_info, width=360).output_file()


class CoverThumbField(CoverField):
    directory = 'cover_thumb'

    @staticmethod
    def transform(wldoc, book):
        from librarian.cover import WLCover
        return WLCover(wldoc.book_info, height=193).output_file()


class CoverApiThumbField(CoverField):
    directory = 'cover_api_thumb'

    @staticmethod
    def transform(wldoc, book):
        from librarian.cover import WLNoBoxCover
        return WLNoBoxCover(wldoc.book_info, height=500).output_file()


class SimpleCoverField(CoverField):
    directory = 'cover_simple'

    @staticmethod
    def transform(wldoc, book):
        from librarian.cover import WLNoBoxCover
        return WLNoBoxCover(wldoc.book_info, height=1000).output_file()


class CoverEbookpointField(CoverField):
    directory = 'cover_ebookpoint'

    @staticmethod
    def transform(wldoc, book):
        from librarian.cover import EbookpointCover
        return EbookpointCover(wldoc.book_info).output_file()
