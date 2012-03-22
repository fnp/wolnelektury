from os.path import join, abspath, exists
from django.core.urlresolvers import reverse
from django.db import models
from waiter.settings import WAITER_ROOT, WAITER_URL
from djcelery.models import TaskMeta


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
        # Pre-fetch objects for deletion to avoid minor race condition
        relevant = [o.id for o in cls.objects.filter(path=path)]
        if exists(abs_path):
            cls.objects.filter(id__in=relevant).delete()
            return True
        else:
            return False

    def is_stale(self):
        if self.task is None:
            # Race; just let the other task roll. 
            return False
        try:
            meta = TaskMeta.objects.get(task_id=self.task)
            assert meta.status in (u'PENDING', u'STARTED', u'SUCCESS', u'RETRY')
        except TaskMeta.DoesNotExist:
            # Might happen it's not yet there.
            pass
        except AssertionError:
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
                waited.task = task_creator(cls.abspath(path))
                waited.description = description
                waited.save()
            return reverse("waiter", args=[path])
        return join(WAITER_URL, path)
