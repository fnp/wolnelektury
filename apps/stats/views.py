# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#

from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext

from catalogue.models import Book, BookMedia


def stats_page(request):
    media = BookMedia.objects.count()
    media_types = BookMedia.objects.values('type').\
            annotate(count=Count('type')).\
            order_by('type')
    for mt in media_types:
        mt['size'] = sum(b.file.size for b in BookMedia.objects.filter(type=mt['type']))
        mt['deprecated'] = BookMedia.objects.filter(
            type=mt['type'], source_sha1=None).count() if mt['type'] in ('mp3', 'ogg') else '-'

    return render_to_response('stats/main.html',
                locals(), context_instance=RequestContext(request))
