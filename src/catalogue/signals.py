# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.conf import settings
from django.core.cache import caches
from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from newtagging.models import tags_updated
from .models import BookMedia, Book, Collection, Fragment, Tag


####
# BookMedia
####


@receiver([post_save, post_delete], sender=BookMedia)
def bookmedia_save(sender, instance, **kwargs):
    instance.book.set_audio_length()
    instance.book.save()


####
# Collection
####


@receiver(post_save, sender=Collection)
def collection_save(sender, instance, **kwargs):
    caches[settings.CACHE_MIDDLEWARE_ALIAS].clear()


####
# Book
####


@receiver(post_save, sender=Book)
def book_save(sender, instance, **kwargs):
    # Books come out anywhere.
    caches[settings.CACHE_MIDDLEWARE_ALIAS].clear()
    # deleting selectively is too much work
    try:
        caches['template_fragments'].clear()
    except ImproperlyConfigured:
        pass
    instance.clear_cache()


@receiver(post_delete, sender=Book)
def book_delete(sender, instance, **kwargs):
    caches[settings.CACHE_MIDDLEWARE_ALIAS].clear()


####
# Tag
####


@receiver(Tag.after_change)
def tag_after_change(sender, instance, **kwargs):
    caches[settings.CACHE_MIDDLEWARE_ALIAS].clear()

    for book in Book.tagged.with_all([instance]).only('pk'):
        book.clear_cache()


@receiver(tags_updated)
def receive_tags_updated(sender, instance, affected_tags, **kwargs):
    categories = set(tag.category for tag in affected_tags if tag.category not in ('set', 'book'))
    if not categories:
        return

    caches[settings.CACHE_MIDDLEWARE_ALIAS].clear()
    if sender in (Book,):
        instance.clear_cache()
