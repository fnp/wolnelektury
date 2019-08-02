# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.core.cache import caches
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from funding.models import Spent
from infopages.models import InfoPage
from libraries.models import Catalog, Library
from pdcounter.models import Author, BookStub


@receiver([post_save, post_delete])
def flush_views_after_manual_change(sender, **kwargs):
    """Flushes views cache after changes with some models.

    Changes to those models happen infrequently, so we can afford
    to just flush the cache on those instances.

    If changes become too often, relevant bits should be separated
    and cached and flushed individually when needed.

    """
    if sender in (Catalog, Library, InfoPage, Author, BookStub, Spent):
        caches[settings.CACHE_MIDDLEWARE_ALIAS].clear()
