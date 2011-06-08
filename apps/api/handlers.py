# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from functools import wraps

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from piston.handler import BaseHandler
from piston.utils import rc, validate
from catalogue.models import Book
from catalogue.forms import BookImportForm


def method_decorator(function_decorator):
    """
        Turns a function(*args, **kwargs) decorator into an
        equivalent decorator for method(self, *args, **kwargs).
    """
    @wraps(function_decorator)
    def decorator(method):
        @wraps(method)
        def decorated_method(self, *args, **kwargs):
            def method_as_function(*fargs, **fkwargs):
                return method(self, *fargs, **fkwargs)
            return function_decorator(method_as_function)(*args, **kwargs)
        return decorated_method
    return decorator


class BookHandler(BaseHandler):
    model = Book
    fields = ('slug', 'title')

    def read(self, request, slug=None):
        if slug:
            return get_object_or_404(Book, slug=slug)
        else:
            return Book.objects.all()

    @method_decorator(permission_required('catalogue.add_book'))
    def create(self, request):
        form = BookImportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return rc.CREATED
        else:
            return rc.BAD_REQUEST

