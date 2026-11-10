# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
import codecs
import csv
from functools import wraps
from io import BytesIO
import os
import re

from django.conf import settings
from django.contrib import admin
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import get_language
from django.conf import settings
from django.utils.safestring import mark_safe


def utc_for_js(dt):
    return dt.strftime('%Y/%m/%d %H:%M:%S UTC')


def makedirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def send_noreply_mail(subject, message, recipient_list, **kwargs):
    send_mail(
        '[WolneLektury] ' + subject,
        message + "\n\n-- \nWiadomość wysłana automatycznie. Prosimy nie odpowiadać.",
        'no-reply@wolnelektury.pl', recipient_list, **kwargs)


# source: https://docs.python.org/2/library/csv.html#examples
class UnicodeCSVWriter(object):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = BytesIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# the original re.escape messes with unicode
def re_escape(s):
    return re.sub(r"[(){}\[\].*?|^$\\+-]", r"\\\g<0>", s)


def get_cached_render_key(instance, property_name, language=None):
    if language is None:
        language = get_language()
    return 'cached_render:%s.%s:%s:%s' % (
            type(instance).__name__,
            property_name,
            instance.pk,
            language
        )


def cached_render(template_name, timeout=24 * 60 * 60):
    def decorator(method):
        @wraps(method)
        def wrapper(self):
            key = get_cached_render_key(self, method.__name__)
            content = cache.get(key)
            if content is None:
                context = method(self)
                content = render_to_string(template_name, context)
                cache.set(key, str(content), timeout=timeout)
            else:
                content = mark_safe(content)
            return content
        return wrapper
    return decorator


def clear_cached_renders(bound_method):
    for lc, ln in settings.LANGUAGES:
        cache.delete(
            get_cached_render_key(
                bound_method.__self__,
                bound_method.__name__,
                lc
            )
        )


class YesNoFilter(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        return (
            ('yes', 'Tak'),
            ('no', 'Nie'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(self.q)
        elif self.value() == 'no':
            return queryset.exclude(self.q)


def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'
