# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.core.cache import caches
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ssify import flush_ssi_includes
from newtagging.models import tags_updated
from picture.models import Picture, PictureArea
from .models import BookMedia, Book, Collection, Fragment, Tag


####
# BookMedia
####


@receiver([post_save, post_delete], sender=BookMedia)
def bookmedia_save(sender, instance, **kwargs):
    instance.book.save()


####
# Collection
####


@receiver(post_save, sender=Collection)
def collection_save(sender, instance, **kwargs):
    caches[settings.CACHE_MIDDLEWARE_ALIAS].clear()
    flush_ssi_includes([
        '/katalog/%s.json' % lang
        for lang in [lc for (lc, _ln) in settings.LANGUAGES]])


@receiver(post_delete, sender=Collection)
def collection_delete(sender, instance, **kwargs):
    flush_ssi_includes([
        '/katalog/%s.json' % lang
        for lang in [lc for (lc, _ln) in settings.LANGUAGES]])

####
# Book
####


@receiver(post_save, sender=Book)
def book_save(sender, instance, **kwargs):
    # Books come out anywhere.
    caches[settings.CACHE_MIDDLEWARE_ALIAS].clear()
    instance.flush_includes()


@receiver(post_delete, sender=Book)
def book_delete(sender, instance, **kwargs):
    caches[settings.CACHE_MIDDLEWARE_ALIAS].clear()
    flush_ssi_includes([
        '/katalog/%s.json' % lang
        for lang in [lc for (lc, _ln) in settings.LANGUAGES]])

    if not settings.NO_SEARCH_INDEX:
        # remove the book from search index, when it is deleted.
        from search.index import Index
        idx = Index()
        idx.remove_book(instance)
        idx.index_tags()


####
# Tag
####


@receiver(Tag.after_change)
def tag_after_change(sender, instance, languages, **kwargs):
    caches[settings.CACHE_MIDDLEWARE_ALIAS].clear()
    flush_ssi_includes([
        '/katalog/%s.json' % lang
        for lang in [lc for (lc, _ln) in settings.LANGUAGES]])

    for model in Book, Picture:
        for model_instance in model.tagged.with_all([instance]).only('pk'):
            model_instance.flush_includes()

    if instance.category == 'author':
        for model in Fragment, PictureArea:
            for model_instance in model.tagged.with_all([instance]).only('pk'):
                model_instance.flush_includes()


@receiver(tags_updated)
def receive_tags_updated(sender, instance, affected_tags, **kwargs):
    categories = set(tag.category for tag in affected_tags if tag.category not in ('set', 'book'))
    if not categories:
        return

    caches[settings.CACHE_MIDDLEWARE_ALIAS].clear()
    instance.flush_includes()
    flush_ssi_includes([
        '/katalog/%s.json' % lang
        for lang in [lc for (lc, _ln) in settings.LANGUAGES]])
