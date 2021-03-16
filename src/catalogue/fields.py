# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.fields.files import FieldFile
from catalogue import app_settings
from catalogue.constants import LANGUAGES_3TO2, EBOOK_FORMATS_WITH_CHILDREN, EBOOK_FORMATS_WITHOUT_CHILDREN
from catalogue.utils import remove_zip, truncate_html_words, gallery_path, gallery_url
from celery.task import Task, task
from celery.utils.log import get_task_logger
from waiter.utils import clear_cache

task_logger = get_task_logger(__name__)

ETAG_SCHEDULED_SUFFIX = '-scheduled'
EBOOK_BUILD_PRIORITY = 0
EBOOK_REBUILD_PRIORITY = 9


class EbookFieldFile(FieldFile):
    """Represents contents of an ebook file field."""

    def build(self):
        """Build the ebook immediately."""
        return self.field.builder.build(self)

    def build_delay(self, priority=EBOOK_BUILD_PRIORITY):
        """Builds the ebook in a delayed task."""
        self.update_etag(
            "".join([self.field.get_current_etag(), ETAG_SCHEDULED_SUFFIX])
        )
        return self.field.builder.apply_async(
            [self.instance, self.field.attname],
            priority=priority
        )

    def get_url(self):
        return self.instance.media_url(self.field.attname.split('_')[0])

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
    registry = []

    def __init__(self, format_name, *args, **kwargs):
        super(EbookField, self).__init__(*args, **kwargs)
        self.format_name = format_name

    def deconstruct(self):
        name, path, args, kwargs = super(EbookField, self).deconstruct()
        args.insert(0, self.format_name)
        return name, path, args, kwargs

    @property
    def builder(self):
        """Finds a celery task suitable for the format of the field."""
        return BuildEbook.for_format(self.format_name)

    def contribute_to_class(self, cls, name):
        super(EbookField, self).contribute_to_class(cls, name)

        self.etag_field_name = f'{name}_etag'

        def has(model_instance):
            return bool(getattr(model_instance, self.attname, None))
        has.__doc__ = None
        has.__name__ = str("has_%s" % self.attname)
        has.short_description = self.name
        has.boolean = True

        self.registry.append(self)

        setattr(cls, 'has_%s' % self.attname, has)

    def get_current_etag(self):
        import pkg_resources
        librarian_version = pkg_resources.get_distribution("librarian").version
        return librarian_version

    def schedule_stale(self, queryset=None):
        """Schedule building this format for all the books where etag is stale."""
        # If there is not ETag field, bail. That's true for xml file field.
        if not hasattr(self.model, f'{self.attname}_etag'):
            return

        etag = self.get_current_etag()
        if queryset is None:
            queryset = self.model.objects.all()

        if self.format_name in EBOOK_FORMATS_WITHOUT_CHILDREN + ['html']:
            queryset = queryset.filter(children=None)

        queryset = queryset.exclude(**{
            f'{self.etag_field_name}__in': [
                etag, f'{etag}{ETAG_SCHEDULED_SUFFIX}'
            ]
        })
        for obj in queryset:
            fieldfile = getattr(obj, self.attname)
            priority = EBOOK_REBUILD_PRIORITY if fieldfile else EBOOK_BUILD_PRIORITY
            fieldfile.build_delay(priority=priority)

    @classmethod
    def schedule_all_stale(cls):
        """Schedules all stale ebooks of all formats to rebuild."""
        for field in cls.registry:
            field.schedule_stale()



class BuildEbook(Task):
    formats = {}

    @classmethod
    def register(cls, format_name):
        """A decorator for registering subclasses for particular formats."""
        def wrapper(builder):
            cls.formats[format_name] = builder
            return builder
        return wrapper

    @classmethod
    def for_format(cls, format_name):
        """Returns a celery task suitable for specified format."""
        return cls.formats.get(format_name, BuildEbookTask)

    @staticmethod
    def transform(wldoc, fieldfile):
        """Transforms an librarian.WLDocument into an librarian.OutputFile.

        By default, it just calls relevant wldoc.as_??? method.

        """
        return getattr(wldoc, "as_%s" % fieldfile.field.format_name)()

    def run(self, obj, field_name):
        """Just run `build` on FieldFile, can't pass it directly to Celery."""
        fieldfile = getattr(obj, field_name)

        # Get etag value before actually building the file.
        etag = fieldfile.field.get_current_etag()
        task_logger.info("%s -> %s@%s" % (obj.slug, field_name, etag))
        ret = self.build(getattr(obj, field_name))
        fieldfile.update_etag(etag)
        obj.clear_cache()
        return ret

    def set_file_permissions(self, fieldfile):
        if fieldfile.instance.preview:
            fieldfile.set_readable(False)

    def build(self, fieldfile):
        book = fieldfile.instance
        out = self.transform(book.wldocument(), fieldfile)
        fieldfile.save(None, File(open(out.get_filename(), 'rb')), save=False)
        self.set_file_permissions(fieldfile)
        if book.pk is not None:
            book.save(update_fields=[fieldfile.field.attname])
        if fieldfile.field.format_name in app_settings.FORMAT_ZIPS:
            remove_zip(app_settings.FORMAT_ZIPS[fieldfile.field.format_name])
# Don't decorate BuildEbook, because we want to subclass it.
BuildEbookTask = task(BuildEbook, ignore_result=True)


@BuildEbook.register('txt')
@task(ignore_result=True)
class BuildTxt(BuildEbook):
    @staticmethod
    def transform(wldoc, fieldfile):
        return wldoc.as_text()


@BuildEbook.register('pdf')
@task(ignore_result=True)
class BuildPdf(BuildEbook):
    @staticmethod
    def transform(wldoc, fieldfile):
        return wldoc.as_pdf(
            morefloats=settings.LIBRARIAN_PDF_MOREFLOATS, cover=True,
            base_url=gallery_url(wldoc.book_info.url.slug), customizations=['notoc'])

    def build(self, fieldfile):
        BuildEbook.build(self, fieldfile)
        clear_cache(fieldfile.instance.slug)


@BuildEbook.register('epub')
@task(ignore_result=True)
class BuildEpub(BuildEbook):
    @staticmethod
    def transform(wldoc, fieldfile):
        return wldoc.as_epub(cover=True, base_url=gallery_url(wldoc.book_info.url.slug))


@BuildEbook.register('mobi')
@task(ignore_result=True)
class BuildMobi(BuildEbook):
    @staticmethod
    def transform(wldoc, fieldfile):
        return wldoc.as_mobi(cover=True, base_url=gallery_url(wldoc.book_info.url.slug))


@BuildEbook.register('html')
@task(ignore_result=True)
class BuildHtml(BuildEbook):
    def build(self, fieldfile):
        from django.core.files.base import ContentFile
        from slugify import slugify
        from sortify import sortify
        from librarian import html
        from catalogue.models import Fragment, Tag

        book = fieldfile.instance

        html_output = self.transform(book.wldocument(parse_dublincore=False), fieldfile)

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
    def transform(wldoc, fieldfile):
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
        return wldoc.as_html(gallery_path=gal_path, gallery_url=gal_url, base_url=gal_url)


class BuildCover(BuildEbook):
    def set_file_permissions(self, fieldfile):
        pass


@BuildEbook.register('cover_thumb')
@task(ignore_result=True)
class BuildCoverThumb(BuildCover):
    @classmethod
    def transform(cls, wldoc, fieldfile):
        from librarian.cover import WLCover
        return WLCover(wldoc.book_info, height=193).output_file()


@BuildEbook.register('cover_api_thumb')
@task(ignore_result=True)
class BuildCoverApiThumb(BuildCover):
    @classmethod
    def transform(cls, wldoc, fieldfile):
        from librarian.cover import WLNoBoxCover
        return WLNoBoxCover(wldoc.book_info, height=500).output_file()


@BuildEbook.register('simple_cover')
@task(ignore_result=True)
class BuildSimpleCover(BuildCover):
    @classmethod
    def transform(cls, wldoc, fieldfile):
        from librarian.cover import WLNoBoxCover
        return WLNoBoxCover(wldoc.book_info, height=1000).output_file()


@BuildEbook.register('cover_ebookpoint')
@task(ignore_result=True)
class BuildCoverEbookpoint(BuildCover):
    @classmethod
    def transform(cls, wldoc, fieldfile):
        from librarian.cover import EbookpointCover
        return EbookpointCover(wldoc.book_info).output_file()


# not used, but needed for migrations
class OverwritingFieldFile(FieldFile):
    """
        Deletes the old file before saving the new one.
    """

    def save(self, name, content, *args, **kwargs):
        leave = kwargs.pop('leave', None)
        # delete if there's a file already and there's a new one coming
        if not leave and self and (not hasattr(content, 'path') or content.path != self.path):
            self.delete(save=False)
        return super(OverwritingFieldFile, self).save(name, content, *args, **kwargs)


class OverwritingFileField(models.FileField):
    attr_class = OverwritingFieldFile


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return name
