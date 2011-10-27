# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import re
import sys
from cPickle import load, dump
from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.management.color import color_style
import zipfile

from catalogue.models import Book, Tag


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-t', '--tags', dest='tags', metavar='SLUG,...',
            help='Use only books tagged with this tags'),
        make_option('-i', '--include', dest='include', metavar='SLUG,...',
            help='Include specific books by slug'),
        make_option('-e', '--exclude', dest='exclude', metavar='SLUG,...',
            help='Exclude specific books by slug')
    )
    help = 'Prepare data for Lesmianator.'
    args = '[%s] output_path.zip' % '|'.join(ftypes)

    def handle(self, ftype, path, **options):
        self.style = color_style()
        verbose = int(options.get('verbosity'))
        tags = options.get('tags')
        include = options.get('include')
        exclude = options.get('exclude')

        if ftype in Book.file_types:
            field = "%s_file" % ftype
        else:
            print self.style.ERROR('Unknown file type.')
            return

        books = []

        if include:
            books += list(Book.objects.filter(slug__in=include.split(',')).only('slug', field))

        if tags:
            books += list(Book.tagged.with_all(Tag.objects.filter(slug__in=tags.split(','))).only('slug', field))
        elif not include:
            books = list(Book.objects.all().only('slug', field))

        if exclude:
            books = [book for book in books if book.slug not in exclude.split(',')]

        archive = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)

        processed = skipped = 0
        for book in books:
            if verbose >= 2:
                print 'Parsing', book.slug
            content = getattr(book, field)
            if not content:
                if verbose >= 1:
                    print self.style.NOTICE('%s has no %s file' % (book.slug, ftype))
                skipped += 1
                continue
            archive.write(content.path, str('%s.%s' % (book.slug, ftype)))
            processed += 1
        archive.close()

        if not processed:
            if skipped:
                print self.style.ERROR("No books with %s files found" % ftype)
            else:
                print self.style.ERROR("No books found")
            return

        if verbose >= 1:
            print "%d processed, %d skipped" % (processed, skipped)
            print "Results written to %s" % path
