# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.

from datetime import datetime, timedelta
from piston.handler import BaseHandler
from django.conf import settings

from api.helpers import timestamp
from api.models import Deleted
from catalogue.models import Book, Tag


class CatalogueHandler(BaseHandler):

    @staticmethod
    def fields(request, name):
        fields_str = request.GET.get(name) if request is not None else None
        return fields_str.split(',') if fields_str is not None else None

    @staticmethod
    def until(t=None):
        """ Returns time suitable for use as upper time boundary for check.
        
            Defaults to 'five minutes ago' to avoid issues with time between
            change stamp set and model save.
            Cuts the microsecond part to avoid issues with DBs where time has
            more precision.

        """
        # set to five minutes ago, to avoid concurrency issues
        if t is None:
            t = datetime.now() - timedelta(seconds=settings.API_WAIT)
        # set to whole second in case DB supports something smaller
        return t.replace(microsecond=0)

    @staticmethod
    def book_dict(book, fields=None):
        all_fields = ('url', 'title', 'description',
                      'gazeta_link', 'wiki_link',
                      'xml', 'epub', 'txt', 'pdf', 'html',
                      'mp3', 'ogg', 'daisy',
                      'parent', 'parent_number',
                      'tags',
                      'license', 'license_description', 'source_name',
                      'technical_editors', 'editors',
                      'author', 'sort_key',
                     )
        if fields:
            fields = (f for f in fields if f in all_fields)
        else:
            fields = all_fields

        extra_info = book.get_extra_info_value()

        obj = {}
        for field in fields:

            if field in ('xml', 'epub', 'txt', 'pdf', 'html'):
                f = getattr(book, field+'_file')
                if f:
                    obj[field] = {
                        'url': f.url,
                        'size': f.size,
                    }

            elif field in ('mp3', 'ogg', 'daisy'):
                media = []
                for m in book.media.filter(type=field):
                    media.append({
                        'url': m.file.get_absolute_url(),
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
            if tag.get_count():
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

    def read(self, request, since):
        return self.book_changes(request, since)


class TagChangesHandler(CatalogueHandler):
    allowed_methods = ('GET',)

    def read(self, request, since):
        return self.tag_changes(request, since)


class ChangesHandler(CatalogueHandler):
    allowed_methods = ('GET',)

    def read(self, request, since):
        return self.changes(request, since)
