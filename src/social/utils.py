# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from collections import defaultdict
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.functional import lazy
from catalogue.models import Book, Tag
from catalogue import utils
from catalogue.tasks import touch_tag
from social.models import Cite


def likes(user, work, request=None):
    if not user.is_authenticated():
        return False

    if request is None:
        return work.tags.filter(category='set', user=user).exists()

    if not hasattr(request, 'social_likes'):
        # tuple: unchecked, checked, liked
        request.social_likes = defaultdict(lambda:(set(), set(), set()))

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
                likes_t[2].update(Tag.intermediary_table_model.objects.filter(
                    content_type_id=ct.pk, tag__user_id=user.pk,
                    object_id__in=ids
                ).distinct().values_list('object_id', flat=True))
                likes_t[1].update(ids)
            return work.pk in likes_t[2]
        return lazy(_likes, bool)()


def get_set(user, name):
    """Returns a tag for use by the user. Creates it, if necessary."""
    try:
        tag = Tag.objects.get(category='set', user=user, name=name)
    except Tag.DoesNotExist:
        tag = Tag.objects.create(category='set', user=user, name=name,
                slug=utils.get_random_hash(name), sort_key=name.lower())
    return tag


def set_sets(user, work, sets):
    """Set tags used for given work by a given user."""

    old_sets = list(work.tags.filter(category='set', user=user))

    work.tags = sets + list(
            work.tags.filter(~Q(category='set') | ~Q(user=user)))

    for shelf in [shelf for shelf in old_sets if shelf not in sets]:
        touch_tag(shelf)
    for shelf in [shelf for shelf in sets if shelf not in old_sets]:
        touch_tag(shelf)

    # delete empty tags
    Tag.objects.filter(category='set', user=user, items=None).delete()


def cites_for_tags(tags):
    """Returns a QuerySet with all Cites for books with given tags."""
    return Cite.objects.filter(book__in=Book.tagged.with_all(tags))
