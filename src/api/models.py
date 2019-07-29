# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import pre_delete
from django.utils.translation import ugettext_lazy as _

from catalogue.models import Book, Tag


class Deleted(models.Model):
    object_id = models.IntegerField()
    slug = models.SlugField(_('slug'), max_length=120, blank=True, db_index=True)
    content_type = models.ForeignKey(ContentType, models.CASCADE)
    category = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(editable=False, db_index=True)
    deleted_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = (('content_type', 'object_id'),)


def _pre_delete_handler(sender, instance, **kwargs):
    """ save deleted objects for change history purposes """

    if sender in (Book, Tag):
        if sender == Tag:
            if instance.category in ('book', 'set'):
                return
            else:
                category = instance.category
        else:
            category = None
        content_type = ContentType.objects.get_for_model(sender)
        Deleted.objects.create(
            content_type=content_type, object_id=instance.id, created_at=instance.created_at, category=category,
            slug=instance.slug)
pre_delete.connect(_pre_delete_handler)


class BookUserData(models.Model):
    book = models.ForeignKey(Book, models.CASCADE)
    user = models.ForeignKey(User, models.CASCADE)
    complete = models.BooleanField(default=False)
    last_changed = models.DateTimeField(auto_now=True)

    @property
    def state(self):
        return 'complete' if self.complete else 'reading'

    @classmethod
    def update(cls, book, user, state):
        instance, created = cls.objects.get_or_create(book=book, user=user)
        instance.complete = state == 'complete'
        instance.save()
        return instance
from django.conf import settings


KEY_SIZE = 18
SECRET_SIZE = 32

CONSUMER_STATES = (
    ('pending', 'Pending approval'),
    ('accepted', 'Accepted'),
    ('canceled', 'Canceled'),
)


class Nonce(models.Model):
    token_key = models.CharField(max_length=KEY_SIZE)
    consumer_key = models.CharField(max_length=KEY_SIZE)
    key = models.CharField(max_length=255)

    def __str__(self):
        return u"Nonce %s for %s" % (self.key, self.consumer_key)


class Consumer(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    key = models.CharField(max_length=KEY_SIZE)
    secret = models.CharField(max_length=SECRET_SIZE)
    status = models.CharField(max_length=16, choices=CONSUMER_STATES, default='pending')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, null=True, blank=True, related_name='consumers')

    def __str__(self):
        return u"Consumer %s with key %s" % (self.name, self.key)


class Token(models.Model):
    REQUEST = 1
    ACCESS = 2
    TOKEN_TYPES = ((REQUEST, u'Request'), (ACCESS, u'Access'))

    key = models.CharField(max_length=KEY_SIZE)
    secret = models.CharField(max_length=SECRET_SIZE)
    token_type = models.IntegerField(choices=TOKEN_TYPES)
    timestamp = models.IntegerField()
    is_approved = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, null=True, blank=True, related_name='tokens')
    consumer = models.ForeignKey(Consumer, models.CASCADE)

    def __str__(self):
        return u"%s Token %s for %s" % (self.get_token_type_display(), self.key, self.consumer)
