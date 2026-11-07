# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from rest_framework import serializers
from api.fields import AbsoluteURLField
from catalogue.models import Book
from club.models import Membership
from social.models import UserList


class BookLiked(serializers.ReadOnlyField):
    def __init__(self, source='pk', **kwargs):
        super(BookLiked, self).__init__(source=source, **kwargs)

    def to_representation(self, value):
        request = self.context['request']
        if not hasattr(request, 'liked_books'):
            if request.user.is_authenticated:
                like_list = UserList.get_favorites_list(user=request.user)
                if like_list is not None:
                    request.liked_books = [b.id for b in like_list.get_books()]
                else:
                    request.liked_books = []
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
