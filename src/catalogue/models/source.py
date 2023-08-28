# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models


class Source(models.Model):
    """A collection of books, which might be defined before publishing them."""
    netloc = models.CharField('położenie sieciowe', max_length=120, primary_key=True)
    name = models.CharField('nazwa', max_length=120, blank=True)

    class Meta:
        ordering = ('netloc',)
        verbose_name = 'źródło'
        verbose_name_plural = 'źródła'
        app_label = 'catalogue'

    def __str__(self):
        return self.netloc

    def save(self, *args, **kwargs):
        from catalogue.models import Book
        try:
            str(self.pk)
            old_self = type(self).objects.get(pk=self)
        except type(self).DoesNotExist:
            old_name = ''
            old_netloc = self.netloc
        else:
            old_name = old_self.name
            old_netloc = old_self.netloc

        ret = super(Source, self).save(*args, **kwargs)

        # If something really changed here, find relevant books
        # and invalidate their cached includes.
        if old_name != self.name or old_netloc != self.netloc:
            for book in Book.objects.all():
                source = book.get_extra_info_json().get('source_url', '')
                if self.netloc in source or (old_netloc != self.netloc and old_netloc in source):
                    book.clear_cache()
        return ret
