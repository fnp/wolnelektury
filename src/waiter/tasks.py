# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from celery.signals import task_postrun
from waiter.models import WaitedFile


def task_delete_after(task_id=None, **kwargs):
    WaitedFile.objects.filter(task_id=task_id).delete()
task_postrun.connect(task_delete_after)
