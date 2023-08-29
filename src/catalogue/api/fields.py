# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from rest_framework import serializers
from api.fields import AbsoluteURLField
from catalogue.models import Book
from club.models import Membership


class BookLiked(serializers.ReadOnlyField):
    def __init__(self, source='pk', **kwargs):
        super(BookLiked, self).__init__(source=source, **kwargs)

    def to_representation(self, value):
        request = self.context['request']
        if not hasattr(request, 'liked_books'):
            if request.user.is_authenticated:
                request.liked_books = set(
                    Book.tagged.with_any(request.user.tag_set.all()).values_list('id', flat=True)
                )
            else:
                request.liked_books = None
        if request.liked_books is not None:
            return value in request.liked_books


class EmbargoURLField(AbsoluteURLField):
    def to_representation(self, value):
        request = self.context['request']
        # FIXME: See #3955.
        if True or Membership.is_active_for(request.user):
            return super().to_representation(value)
        else:
            return None
