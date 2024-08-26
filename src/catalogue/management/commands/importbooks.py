# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
import os
import sys
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from django.core.files import File
from django.db import transaction
from catalogue.models import Book


class Command(BaseCommand):
    help = 'Imports books from the specified directories.'

    def add_arguments(self, parser):
        parser.add_argument(
                '-q', '--quiet', action='store_false', dest='verbose', default=True,
                help='Verbosity level; 0=minimal output, 1=normal output, 2=all output')
        parser.add_argument(
                '-f', '--force', action='store_true', dest='force',
                default=False, help='Overwrite works already in the catalogue')
        parser.add_argument(
                '-D', '--dont-build', dest='dont_build', metavar="FORMAT,...",
                help="Skip building specified formats")
        parser.add_argument(
                '-F', '--not-findable', action='store_false',
                dest='findable', default=True,
                help='Set book as not findable.')
        parser.add_argument('directory', nargs='+')

    def import_book(self, file_path, options):
        verbose = options.get('verbose')
        if options.get('dont_build'):
            dont_build = options.get('dont_build').lower().split(',')
        else:
            dont_build = None
        file_base, ext = os.path.splitext(file_path)
        book = Book.from_xml_file(file_path, overwrite=options.get('force'),
                                  dont_build=dont_build,
                                  findable=options.get('findable'),
                                  remote_gallery_url='file://' + os.path.dirname(os.path.abspath(file_base)) + '/img/'
                                  )
        for ebook_format in Book.ebook_formats:
            if os.path.isfile(file_base + '.' + ebook_format):
                getattr(book, '%s_file' % ebook_format).save(
                    '%s.%s' % (book.slug, ebook_format),
                    File(file(file_base + '.' + ebook_format)),
                    save=False
                    )
                if verbose:
                    print("Importing %s.%s" % (file_base, ebook_format))
        book.save()

    @transaction.atomic
    def handle(self, **options):
        self.style = color_style()

        verbose = options.get('verbose')

        files_imported = 0
        files_skipped = 0

        for dir_name in options['directory']:
            if not os.path.isdir(dir_name):
                print(self.style.ERROR("%s: Not a directory. Skipping." % dir_name))
            else:
                # files queue
                files = sorted(os.listdir(dir_name))
                postponed = {}
                while files:
                    file_name = files.pop(0)
                    file_path = os.path.join(dir_name, file_name)
                    file_base, ext = os.path.splitext(file_path)

                    # Skip files that are not XML files
                    if not ext == '.xml':
                        continue

                    if verbose > 0:
                        print("Parsing '%s'" % file_path)
                    else:
                        sys.stdout.write('.')
                        sys.stdout.flush()

                    # Import book files
                    try:
                        self.import_book(file_path, options)
                        files_imported += 1

                    except Book.AlreadyExists:
                        print(self.style.ERROR(
                            '%s: Book already imported. Skipping. To overwrite use --force.' %
                            file_path))
                        files_skipped += 1

                    except Book.DoesNotExist as e:
                        if file_name not in postponed or postponed[file_name] < files_imported:
                            # push it back into the queue, maybe the missing child will show up
                            if verbose:
                                print(self.style.NOTICE('Waiting for missing children'))
                            files.append(file_name)
                            postponed[file_name] = files_imported
                        else:
                            # we're in a loop, nothing's being imported - some child is really missing
                            raise e

        # Print results
        print()
        print("Results: %d files imported, %d skipped, %d total." % (
            files_imported, files_skipped, files_imported + files_skipped))
        print()
