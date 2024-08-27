# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
import os.path
from datetime import date
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.shortcuts import render

from catalogue.models import Book, BookMedia, Tag
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

    licenses = set()
    for b in Book.objects.all().iterator():
        extra_info = b.get_extra_info_json()
        if extra_info.get('license'):
            licenses.add((extra_info.get('license'), extra_info.get('license_description')))

    etags = []
    all_books = Book.objects.all()
    all_books_count = all_books.count()
    noparent_books = Book.objects.filter(children=None)
    noparent_books_count = noparent_books.count()
    for field in Book._meta.fields:
        if not getattr(field, 'with_etag', None): continue
        etag = field.get_current_etag()
        d = {
            'field': field.name,
            'etag': etag,
        }
        if field.for_parents:
            books = all_books
            n_books = all_books_count
        else:
            books = noparent_books
            n_books = noparent_books_count
        tags = books.values_list(field.etag_field.name).order_by(
            '-' + field.etag_field.name).distinct().annotate(c=Count('*'))
        d['tags'] = [
            {
                'tag': t[0],
                'count': t[1],
                'perc': round(100 * t[1] / n_books, 2)
            }
            for t in tags
        ]
        etags.append(d)

    unused_tags = Tag.objects.exclude(category='set').filter(items=None, book=None)
        
    return render(request, 'reporting/main.html', {
        'media_types': media_types,
        'licenses': licenses,
        'etags': etags,
        'unused_tags': unused_tags,
    })


@generated_file_view('reports/katalog.pdf', 'application/pdf',
                     send_name=lambda: 'wolnelektury_%s.pdf' % date.today(), signals=[Book.published])
def catalogue_pdf(path):
    books_by_author, orphans, books_by_parent = Book.book_list()
    render_to_pdf(path, 'reporting/catalogue.texml', {
        'books_by_author': books_by_author,
        'orphans': orphans,
        'books_by_parent': books_by_parent,
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
        'books_by_parent': books_by_parent,
    })
