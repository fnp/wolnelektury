# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from rest_framework import serializers
from catalogue.models import Book


class BookLiked(serializers.ReadOnlyField):
    def __init__(self, source='pk', **kwargs):
        super(BookLiked, self).__init__(source=source, **kwargs)

    def to_representation(self, value):
        request = self.context['request']
        if not hasattr(request, 'liked_books'):
            if request.user.is_authenticated():
                request.liked_books = set(Book.tagged.with_any(request.user.tag_set.all()).values_list('id', flat=True))
            else:
                request.liked_books = None
        if request.liked_books is not None:
            return value in request.liked_books
