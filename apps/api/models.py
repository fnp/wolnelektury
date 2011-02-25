# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.db.models.signals import pre_delete

from catalogue.models import Book, Tag


class Deleted(models.Model):
    object_id = models.IntegerField()
    type = models.CharField(max_length="50", db_index=True)
    created_at = models.DateTimeField(editable=False, db_index=True)
    deleted_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = (('type', 'object_id'),)



def _pre_delete_handler(sender, instance, **kwargs):
    """ save deleted objects for change history purposes """

    if sender in (Book, Tag):
        Deleted.objects.create(type=sender.__name__, object_id=instance.id, created_at=instance.created_at)
pre_delete.connect(_pre_delete_handler)
