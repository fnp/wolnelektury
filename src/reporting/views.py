# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import os.path
from datetime import date
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext

from catalogue.models import Book, BookMedia
from reporting.utils import render_to_pdf, render_to_csv, generated_file_view


@staff_member_required
def stats_page(request):
    media_types = BookMedia.objects.values('type').annotate(count=Count('type')).order_by('type')
    for mt in media_types:
        mt['size'] = sum(b.file.size for b in BookMedia.objects.filter(type=mt['type']).iterator())
        if mt['type'] in ('mp3', 'ogg'):
            deprecated = BookMedia.objects.filter(type=mt['type'], source_sha1=None)
            mt['deprecated'] = deprecated.count()
            mt['deprecated_files'] = deprecated.order_by('book', 'name')
        else:
            mt['deprecated'] = '-'

    licenses = set(
        (b.extra_info.get('license'), b.extra_info.get('license_description'))
        for b in Book.objects.all().iterator() if b.extra_info.get('license'))

    return render_to_response('reporting/main.html', {
        'media_types': media_types,
        'licenses': licenses,
    }, context_instance=RequestContext(request))


@generated_file_view('reports/katalog.pdf', 'application/pdf',
                     send_name=lambda: 'wolnelektury_%s.pdf' % date.today(), signals=[Book.published])
def catalogue_pdf(path):
    books_by_author, orphans, books_by_parent = Book.book_list()
    render_to_pdf(path, 'reporting/catalogue.texml', {
        'books_by_author': books_by_author,
        'orphans': orphans,
        'book_by_parent': books_by_parent,
    }, {
        "wl-logo.png": os.path.join(settings.STATIC_ROOT, "img/logo-big.png"),
    })


@generated_file_view('reports/katalog.csv', 'application/csv',
                     send_name=lambda: 'wolnelektury_%s.csv' % date.today(), signals=[Book.published])
def catalogue_csv(path):
    books_by_author, orphans, books_by_parent = Book.book_list()
    render_to_csv(path, 'reporting/catalogue.csv', {
        'books_by_author': books_by_author,
        'orphans': orphans,
        'book_by_parent': books_by_parent,
    })
