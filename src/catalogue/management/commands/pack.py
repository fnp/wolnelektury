# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import zipfile
from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from catalogue.models import Book, Tag


class Command(BaseCommand):
    help = 'Prepare ZIP package with files of given type.'

    def add_arguments(self, parser):
        parser.add_argument(
                '-t', '--tags', dest='tags', metavar='SLUG,...',
                help='Use only books tagged with this tags')
        parser.add_argument(
                '-i', '--include', dest='include', metavar='SLUG,...',
                help='Include specific books by slug')
        parser.add_argument(
                '-e', '--exclude', dest='exclude', metavar='SLUG,...',
                help='Exclude specific books by slug')
        parser.add_argument(
                '--top-level', dest='top_level', action='store_true')
        parser.add_argument('ftype', metavar='|'.join(Book.formats))
        parser.add_argument('path', metavar='output_path.zip')

    def handle(self, **options):
        self.style = color_style()
        ftype = options['ftype']
        path = options['path']
        verbose = int(options.get('verbosity'))
        tags = options.get('tags')
        include = options.get('include')
        exclude = options.get('exclude')
        top_level = options.get('top_level')

        if ftype in Book.formats:
            field = "%s_file" % ftype
        else:
            print(self.style.ERROR('Unknown file type.'))
            return

        books = []

        if include:
            books += list(Book.objects.filter(slug__in=include.split(',')).only('slug', field))

        if tags:
            books += list(Book.tagged.with_all(Tag.objects.filter(slug__in=tags.split(','))).only('slug', field))
        elif not include:
            books = Book.objects.all()
            if top_level:
                books = books.filter(parent=None)
            books = list(books.only('slug', field))

        if exclude:
            books = [book for book in books if book.slug not in exclude.split(',')]

        archive = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)

        processed = skipped = 0
        for book in books:
            if verbose >= 2:
                print('Parsing', book.slug)
            content = getattr(book, field)
            if not content:
                if verbose >= 1:
                    print(self.style.NOTICE('%s has no %s file' % (book.slug, ftype)))
                skipped += 1
                continue
            archive.write(content.path, str('%s.%s' % (book.slug, ftype)))
            processed += 1
        archive.close()

        if not processed:
            if skipped:
                print(self.style.ERROR("No books with %s files found" % ftype))
            else:
                print(self.style.ERROR("No books found"))
            return

        if verbose >= 1:
            print("%d processed, %d skipped" % (processed, skipped))
            print("Results written to %s" % path)
