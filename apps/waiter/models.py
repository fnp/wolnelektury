# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from os.path import join, isfile
from django.core.urlresolvers import reverse
from django.db import models
from waiter.settings import WAITER_URL, WAITER_MAX_QUEUE
from waiter.utils import check_abspath
from picklefield import PickledObjectField


class WaitedFile(models.Model):
    path = models.CharField(max_length=255, unique=True, db_index=True)
    task_id = models.CharField(max_length=128, db_index=True, null=True, blank=True)
    task = PickledObjectField(null=True, editable=False)
    description = models.CharField(max_length=255, null=True, blank=True)

    @classmethod
    def exists(cls, path):
        """Returns opened file or None.

        `path` is relative to WAITER_ROOT.
        Won't open a path leading outside of WAITER_ROOT.
        """
        abs_path = check_abspath(path)
        # Pre-fetch objects for deletion to avoid minor race condition
        relevant = [o.id for o in cls.objects.filter(path=path)]
        if isfile(abs_path):
            cls.objects.filter(id__in=relevant).delete()
            return True
        else:
            return False

    @classmethod
    def can_order(cls, path):
        return (cls.objects.filter(path=path).exists() or
                cls.exists(path) or
                cls.objects.count() < WAITER_MAX_QUEUE
                )

    def is_stale(self):
        if self.task is None:
            # Race; just let the other task roll.
            return False
        if self.task.status not in (u'PENDING', u'STARTED', u'SUCCESS', u'RETRY'):
            return True
        return False

    @classmethod
    def order(cls, path, task_creator, description=None):
        """
        Returns an URL for the user to follow.
        If the file is ready, returns download URL.
        If not, starts preparing it and returns waiting URL.

        task_creator: function taking a path and generating the file;
        description: a string or string proxy with a description for user;
        """
        already = cls.exists(path)
        if not already:
            waited, created = cls.objects.get_or_create(path=path)
            if created or waited.is_stale():
                waited.task = task_creator(check_abspath(path))
                waited.task_id = waited.task.task_id
                waited.description = description
                waited.save()
            return reverse("waiter", args=[path])
        return join(WAITER_URL, path)
