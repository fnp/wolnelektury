# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.

from datetime import datetime
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import simplejson as json
from piston.handler import BaseHandler
from piston.utils import rc, validate

from api.models import Deleted
from api.helpers import timestamp
from catalogue.models import Book, Tag
from catalogue.forms import BookImportForm
from catalogue.views import tagged_object_list 
"""
class TagHandler(BaseHandler):
   allowed_methods = ('GET',)
   model = Tag   

   def read(self, request, tags=''):
      if tags == '':
        return Tag.objects.all()
      else:
        return tagged_object_list(request, tags, api=True)

class BookHandler(BaseHandler):
    model = Book
    #fields = ('slug', 'title')

    def read(self, request, slug=None):
        if slug:
            return get_object_or_404(Book, slug=slug)
        else:
            return Book.objects.all()
"""


class WLHandler(BaseHandler):

    @staticmethod
    def fields(request, name):
        fields_str = request.GET.get(name) if request is not None else None
        return fields_str.split(',') if fields_str is not None else None

    @staticmethod
    def book_dict(book, fields=None, extra_fields=None):
        obj = {}
        for field in ('slug', 'title', 'description',
                      'extra_info', 'gazeta_link', 'wiki_link'):
            if getattr(book, field):
                obj[field] = getattr(book, field)
        for field in ('created_at', 'changed_at'):
            obj[field] = timestamp(getattr(book, field))
        for field in ('xml', 'epub', 'txt', 'pdf', 'html'):
            f = getattr(book, field+'_file') 
            if f:
                obj[field] = f.url
        for media in book.medias.all():
            obj.setdefault(media.type, []).append(media.file.url)
        if book.parent:
            obj['parent'] = book.parent.id
            obj['parent_number'] = book.parent_number
        if fields is not None:
            for key in obj.keys():
                if key not in fields:
                    del obj[key]

        # if there's still extra_info, we can parse it
        if 'extra_info' in obj:
            extra = json.loads(obj['extra_info'])
            if extra_fields is not None:
                for key in extra.keys():
                    if key not in extra_fields:
                        del extra[key]
            obj['extra_info'] = extra

        obj['id'] = book.id
        return obj

    @classmethod
    def book_changes(cls, since=0, request=None):
        since = datetime.fromtimestamp(float(since))
        book_fields = cls.fields(request, 'book_fields')
        extra_fields = cls.fields(request, 'extra_fields')

        added = []
        changed = []
        deleted = []

        last_change = since
        for book in Book.objects.filter(changed_at__gt=since):
            if book.changed_at > last_change:
                last_change = book.changed_at
            book_d = cls.book_dict(book, book_fields, extra_fields)
            if book.created_at > since:
                added.append(book_d)
            else:
                changed.append(book_d)

        for book in Deleted.objects.filter(type='Book', deleted_at__gt=since, created_at__lte=since):
            if book.deleted_at > last_change:
                last_change = book.deleted_at
            deleted.append(book.id)
        return {'added': added, 'changed': changed, 'deleted': deleted, 'last_change': timestamp(last_change)}

    @staticmethod
    def tag_dict(tag, fields=None):
        obj = {}
        for field in ('name', 'slug', 'sort_key', 'category', 'description', 'main_page', #'created_at', 'changed_at',
                      'gazeta_link', 'wiki_link'):
            if getattr(tag, field):
                obj[field] = getattr(tag, field)
        if fields is not None:
            for key in obj.keys():
                if key not in fields:
                    del obj[key]
        obj['id'] = tag.id
        return obj

    @classmethod
    def tag_changes(cls, since=0, request=None):
        since = datetime.fromtimestamp(float(since))
        tag_fields = cls.fields(request, 'tag_fields')

        added = []
        changed = []
        deleted = []

        last_change = since
        for tag in Tag.objects.filter(changed_at__gt=since):
            if tag.changed_at > last_change:
                last_change = tag.changed_at
            tag_d = cls.tag_dict(tag, tag_fields)
            if tag.created_at > since:
                added.append(tag_d)
            else:
                changed.append(tag_d)

        for tag in Deleted.objects.filter(type='Tag', deleted_at__gt=since, created_at__lte=since):
            if tag.deleted_at > last_change:
                last_change = tag.deleted_at
            deleted.append(tag.id)
        return {'added': added, 'changed': changed, 'deleted': deleted, 'last_change': timestamp(last_change)}


class BookChangesHandler(WLHandler):
    allowed_methods = ('GET',)

    def read(self, request, since):
        return self.book_changes(since, request)


class TagChangesHandler(WLHandler):
    allowed_methods = ('GET',)

    def read(self, request, since):
        return self.tag_changes(since, request)


class ChangesHandler(WLHandler):
    allowed_methods = ('GET',)

    def read(self, request, since):
        changes = {
            'books': self.book_changes(since, request),
            'tags': self.tag_changes(since, request),
        }

        last_change = 0
        changes_rev = {}
        for model in changes:
            for field in changes[model]:
                if field == 'last_change':
                    if changes[model][field] > last_change:
                        last_change = changes[model][field]
                else:
                    changes_rev.setdefault(field, {})[model] = changes[model][field]
        changes_rev['last_change'] = last_change
        return changes_rev



# old
"""
staff_required = user_passes_test(lambda user: user.is_staff)

class BookHandler(BaseHandler):
    model = Book
    fields = ('slug', 'title')

    @staff_required
    def read(self, request, slug=None):
        if slug:
            return get_object_or_404(Book, slug=slug)
        else:
            return Book.objects.all()

    @staff_required
    def create(self, request):
        form = BookImportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return rc.CREATED
        else:
            return rc.BAD_REQUEST
"""
