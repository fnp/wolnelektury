# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from collections import defaultdict
from random import randint

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.functional import lazy
from catalogue.models import Book
from social.models import Cite
from social import models


def likes(user, work, request=None):
    if not user.is_authenticated:
        return False

    if request is None:
        return models.UserList.likes(user, work)

    if not hasattr(request, 'social_likes'):
        # tuple: unchecked, checked, liked
        request.social_likes = defaultdict(lambda: (set(), set(), set()))

    ct = ContentType.objects.get_for_model(type(work))
    likes_t = request.social_likes[ct.pk]
    if work.pk in likes_t[1]:
        return work.pk in likes_t[2]
    else:
        likes_t[0].add(work.pk)

        def _likes():
            if likes_t[0]:
                ids = tuple(likes_t[0])
                likes_t[0].clear()
                ls = models.UserList.get_favorites_list(user)
                if ls is None:
                    return False
                likes_t[2].update(
                    ls.userlistitem_set.filter(deleted=False).filter(
                        book_id__in=ids).values_list('book_id', flat=True))
                likes_t[1].update(ids)
            return work.pk in likes_t[2]
        return lazy(_likes, bool)()


def cites_for_tags(tags):
    """Returns a QuerySet with all Cites for books with given tags."""
    return Cite.objects.filter(book__in=Book.tagged.with_all(tags))


# tag_ids is never used
def choose_cite(book_id=None, tag_ids=None):
    """Choose a cite for main page, for book or for set of tags."""
    if book_id is not None:
        cites = Cite.objects.filter(Q(book=book_id) | Q(book__ancestor=book_id))
    elif tag_ids is not None:
        tags = Tag.objects.filter(pk__in=tag_ids)
        cites = cites_for_tags(tags)
    else:
        cites = Cite.objects.all()
    stickies = cites.filter(sticky=True)
    count = len(stickies)
    if count:
        cites = stickies
    else:
        count = len(cites)
    if count:
        cite = cites[randint(0, count - 1)]
    else:
        cite = None
    return cite


def get_or_choose_cite(request, book_id=None, tag_ids=None):
    try:
        assert request.user.is_staff
        assert 'banner' in request.GET
        return Cite.objects.get(pk=request.GET['banner'])
    except (AssertionError, Cite.DoesNotExist):
        return choose_cite(book_id, tag_ids)
