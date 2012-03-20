from os.path import join, abspath, exists
from django.db import models
from waiter.settings import WAITER_ROOT, WAITER_URL
from django.core.urlresolvers import reverse

class WaitedFile(models.Model):
    path = models.CharField(max_length=255, unique=True, db_index=True)
    task = models.CharField(max_length=64, null=True, editable=False)
    description = models.CharField(max_length=255, null=True, blank=True)

    @staticmethod
    def abspath(path):
        abs_path = abspath(join(WAITER_ROOT, path))
        if not abs_path.startswith(WAITER_ROOT):
            raise ValueError('Path not inside WAITER_ROOT.')
        return abs_path

    @classmethod
    def exists(cls, path):
        """Returns opened file or None.
        
        `path` is relative to WAITER_ROOT.
        Won't open a path leading outside of WAITER_ROOT.
        """
        abs_path = cls.abspath(path)
        # Pre-fetch objects to avoid minor race condition
        relevant = [o.id for o in cls.objects.filter(path=path)]
        print abs_path
        if exists(abs_path):
            cls.objects.filter(id__in=relevant).delete()
            return True
        else:
            return False

    @classmethod
    def order(cls, path, task_creator, description=None):
        """
        Returns an URL for the user to follow.
        If the file is ready, returns download URL.
        If not, starts preparing it and returns waiting URL.
        """
        already = cls.exists(path)
        if not already:
            waited, created = cls.objects.get_or_create(path=path)
            if created:
                # TODO: makedirs
                waited.task = task_creator(cls.abspath(path))
                print waited.task
                waited.description = description
                waited.save()
            # TODO: it the task exists, if stale delete, send some mail and restart
            return reverse("waiter", args=[path])
        return join(WAITER_URL, path)
