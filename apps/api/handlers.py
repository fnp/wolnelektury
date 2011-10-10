# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from functools import wraps

from django.shortcuts import get_object_or_404
from piston.handler import AnonymousBaseHandler, BaseHandler
from piston.utils import rc, validate
from catalogue.models import Book
from catalogue.forms import BookImportForm



class AnonymousBooksHandler(AnonymousBaseHandler):
    model = Book
    fields = ('slug', 'title')

    def read(self, request, slug=None):
        if slug:
            return get_object_or_404(Book, slug=slug)
        else:
            return Book.objects.all()


class BooksHandler(BaseHandler):
    model = Book
    fields = ('slug', 'title')
    anonymous = AnonymousBooksHandler

    def create(self, request):
        if not request.user.has_perm('catalogue.add_book'):
            return rc.FORBIDDEN

        form = BookImportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return rc.CREATED
        else:
            return rc.BAD_REQUEST

