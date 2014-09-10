# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.core.cache import caches
from django.db.models.signals import post_save, pre_delete, post_delete
import django.dispatch
from catalogue.models import Tag, BookMedia, Book, Fragment, Collection
from catalogue import tasks
from catalogue.utils import delete_from_cache_by_language
from newtagging.models import tags_updated


permanent_cache = caches['permanent']


def _pre_delete_handler(sender, instance, **kwargs):
    """ refresh Book on BookMedia delete """
    if sender == BookMedia:
        instance.book.save()
pre_delete.connect(_pre_delete_handler)


def _post_delete_handler(sender, instance, **kwargs):
    """ refresh Book on BookMedia delete """
    if sender == Collection:
        delete_from_cache_by_language(permanent_cache, 'catalogue.collection:%s/%%s' % instance.slug)
        delete_from_cache_by_language(permanent_cache, 'catalogue.catalogue/%s')
post_delete.connect(_post_delete_handler)


def _post_save_handler(sender, instance, **kwargs):
    """ refresh all the short_html stuff on BookMedia update """
    if sender == BookMedia:
        instance.book.save()
        delete_from_cache_by_language(permanent_cache, 'catalogue.audiobook_list/%s')
        delete_from_cache_by_language(permanent_cache, 'catalogue.daisy_list/%s')
    elif sender == Collection:
        delete_from_cache_by_language(permanent_cache, 'catalogue.collection:%s/%%s' % instance.slug)
        delete_from_cache_by_language(permanent_cache, 'catalogue.catalogue/%s')
post_save.connect(_post_save_handler)


def post_publish(sender, **kwargs):
    delete_from_cache_by_language(permanent_cache, 'catalogue.book_list/%s')
    delete_from_cache_by_language(permanent_cache, 'catalogue.catalogue/%s')
Book.published.connect(post_publish)


if not settings.NO_SEARCH_INDEX:
    @django.dispatch.receiver(post_delete, sender=Book)
    def _remove_book_from_index_handler(sender, instance, **kwargs):
        """ remove the book from search index, when it is deleted."""
        from search.index import Index
        idx = Index()
        idx.remove_book(instance)
        idx.index_tags()
