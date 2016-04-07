# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
"""
Wrappers for piston Emitter classes.

When outputting a queryset of selected models, instead of returning
XML or JSON stanzas, SSI include statements are returned.

"""
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models.query import QuerySet
from piston.emitters import Emitter, XMLEmitter, JSONEmitter
from catalogue.models import Book, Fragment, Tag
from django.utils.translation import get_language


class SsiQS(object):
    """A wrapper for QuerySet that won't serialize."""

    def __init__(self, queryset):
        self.queryset = queryset

    def __unicode__(self):
        raise TypeError("This is not serializable.")

    def get_ssis(self, emitter_format):
        """Yields SSI include statements for the queryset."""
        url_pattern = reverse(
            'api_include',
            kwargs={
                'model': self.queryset.model.__name__.lower(),
                'pk': '0000',
                'emitter_format': emitter_format,
                'lang': get_language(),
            })
        for instance in self.queryset:
            yield "<!--#include file='%s'-->" % url_pattern.replace('0000', str(instance.pk))


class SsiEmitterMixin(object):
    def construct(self):
        ssify_api = getattr(settings, 'SSIFY_API', True)
        if ssify_api and isinstance(self.data, QuerySet) and self.data.model in (Book, Fragment, Tag):
            return SsiQS(self.data)
        else:
            return super(SsiEmitterMixin, self).construct()


class SsiJsonEmitter(SsiEmitterMixin, JSONEmitter):
    def render(self, request):
        try:
            return super(SsiJsonEmitter, self).render(request)
        except TypeError:
            return '[%s]' % ",".join(self.construct().get_ssis('json'))

Emitter.register('json', SsiJsonEmitter, 'application/json; charset=utf-8')


class SsiXmlEmitter(SsiEmitterMixin, XMLEmitter):
    def render(self, request):
        try:
            return super(SsiXmlEmitter, self).render(request)
        except TypeError:
            return '<?xml version="1.0" encoding="utf-8"?>\n' \
                '<response><resource>%s</resource></response>' % \
                '</resource><resource>'.join(self.construct().get_ssis('xml'))

Emitter.register('xml', SsiXmlEmitter, 'text/xml; charset=utf-8')
