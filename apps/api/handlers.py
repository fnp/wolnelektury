# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.

from datetime import datetime
from piston.handler import BaseHandler

from api.helpers import timestamp
from api.models import Deleted
from catalogue.models import Book, Tag

class CatalogueHandler(BaseHandler):

    @staticmethod
    def fields(request, name):
        fields_str = request.GET.get(name) if request is not None else None
        return fields_str.split(',') if fields_str is not None else None

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
                for m in book.medias.filter(type=''):
                    files.append({
                        'url': m.file.get_absolute_url(),
                        'size': m.file.size,
                    })
                if media:
                    obj[field] = media

            elif field == 'url':
                obj[field] = book.get_absolute_url()

            elif field == 'tags':
                obj[field] = [t.id for t in book.tags.exclude(category__in=('book', 'set'))]

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
    def book_changes(cls, since=0, request=None, fields=None):
        since = datetime.fromtimestamp(int(since))
        if not fields:
            fields = cls.fields(request, 'book_fields')

        added = []
        updated = []
        deleted = []

        last_change = since
        for book in Book.objects.filter(changed_at__gte=since):
            book_d = cls.book_dict(book, fields)
            updated.append(book_d)

        for book in Deleted.objects.filter(content_type=Book, deleted_at__gte=since, created_at__lt=since):
            deleted.append(book.id)
        return {'updated': updated, 'deleted': deleted}

    @staticmethod
    def tag_dict(tag, fields=None):
        all_fields = ('name', 'category', 'sort_key', 'description',
                      'gazeta_link', 'wiki_link',
                      'url',
                     )

        if fields:
            fields = (f for f in fields if f in all_fields)
        else:
            fields = all_fields

        obj = {}
        for field in fields:

            if field == 'url':
                obj[field] = tag.get_absolute_url()

            else:
                f = getattr(tag, field)
                if f:
                    obj[field] = f

        obj['id'] = tag.id
        return obj

    @classmethod
    def tag_changes(cls, since=0, request=None, fields=None, categories=None):
        since = datetime.fromtimestamp(int(since))
        if not fields:
            fields = cls.fields(request, 'tag_fields')
        if not categories:
            categories = cls.fields(request, 'tag_categories')

        all_categories = ('author', 'theme', 'epoch', 'kind', 'genre')
        if categories:
            categories = (c for c in categories if c in all_categories)
        else:
            categories = all_categories

        updated = []
        deleted = []

        for tag in Tag.objects.filter(category__in=categories, changed_at__gte=since):
            tag_d = cls.tag_dict(tag, fields)
            updated.append(tag_d)

        for tag in Deleted.objects.filter(category__in=categories,
                content_type=Tag, deleted_at__gte=since, created_at__lt=since):
            deleted.append(tag.id)
        return {'updated': updated, 'deleted': deleted}

    @classmethod
    def changes(cls, since=0, request=None, book_fields=None,
                tag_fields=None, tag_categories=None):
        changes = {
            'time_checked': timestamp(datetime.now())
        }

        changes_by_type = {
            'books': cls.book_changes(since, request, book_fields),
            'tags': cls.tag_changes(since, request, tag_fields, tag_categories),
        }

        for model in changes_by_type:
            for field in changes_by_type[model]:
                changes.setdefault(field, {})[model] = changes_by_type[model][field]
        return changes


class BookChangesHandler(CatalogueHandler):
    allowed_methods = ('GET',)

    def read(self, request, since):
        return self.book_changes(since, request)


class TagChangesHandler(CatalogueHandler):
    allowed_methods = ('GET',)

    def read(self, request, since):
        return self.tag_changes(since, request)


class ChangesHandler(CatalogueHandler):
    allowed_methods = ('GET',)

    def read(self, request, since):
        return self.changes(since, request)
