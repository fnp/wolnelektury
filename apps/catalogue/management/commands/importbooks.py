# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import os
import sys
from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from django.core.files import File

from catalogue.models import Book


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-q', '--quiet', action='store_false', dest='verbose', default=True,
            help='Verbosity level; 0=minimal output, 1=normal output, 2=all output'),
        make_option('-f', '--force', action='store_true', dest='force', default=False,
            help='Print status messages to stdout')
    )
    help = 'Imports books from the specified directories.'
    args = 'directory [directory ...]'

    def handle(self, *directories, **options):
        from django.db import transaction

        self.style = color_style()

        verbose = options.get('verbose')
        force = options.get('force')
        show_traceback = options.get('traceback', False)

        # Start transaction management.
        transaction.commit_unless_managed()
        transaction.enter_transaction_management()
        transaction.managed(True)

        files_imported = 0
        files_skipped = 0
        
        for dir_name in directories:
            if not os.path.isdir(dir_name):
                print self.style.ERROR("%s: Not a directory. Skipping." % dir_name)
            else:
                for file_name in os.listdir(dir_name):
                    file_path = os.path.join(dir_name, file_name)
                    file_base, ext = os.path.splitext(file_path)
                    
                    # Skip files that are not XML files
                    if not ext == '.xml':
                        continue
                    
                    if verbose > 0:
                        print "Parsing '%s'" % file_path
                    else:
                        sys.stdout.write('.')
                        sys.stdout.flush()
                    
                    # Import book files
                    try:
                        book = Book.from_xml_file(file_path, overwrite=force)
                        files_imported += 1
                        
                        if os.path.isfile(file_base + '.pdf'):
                            book.pdf_file.save('%s.pdf' % book.slug, File(file(file_base + '.pdf')))
                            if verbose:
                                print "Importing %s.pdf" % file_base 
                        if os.path.isfile(file_base + '.epub'):
                            book.epub_file.save('%s.epub' % book.slug, File(file(file_base + '.epub')))
                            if verbose:
                                print "Importing %s.epub" % file_base 
                        if os.path.isfile(file_base + '.odt'):
                            book.odt_file.save('%s.odt' % book.slug, File(file(file_base + '.odt')))
                            if verbose:
                                print "Importing %s.odt" % file_base
                        if os.path.isfile(file_base + '.txt'):
                            book.txt_file.save('%s.txt' % book.slug, File(file(file_base + '.txt')))
                            if verbose:
                                print "Importing %s.txt" % file_base
                        if os.path.isfile(os.path.join(dir_name, book.slug + '.mp3')):
                            book.mp3_file.save('%s.mp3' % book.slug, File(file(os.path.join(dir_name, book.slug + '.mp3'))))
                            if verbose:
                                print "Importing %s.mp3" % book.slug
                        if os.path.isfile(os.path.join(dir_name, book.slug + '.ogg')):
                            book.ogg_file.save('%s.ogg' % book.slug, File(file(os.path.join(dir_name, book.slug + '.ogg'))))
                            if verbose:
                                print "Importing %s.ogg" % book.slug
                            
                        book.save()
                    
                    except Book.AlreadyExists, msg:
                        print self.style.ERROR('%s: Book already imported. Skipping. To overwrite use --force.' %
                            file_path)
                        files_skipped += 1
                        
        # Print results
        print
        print "Results: %d files imported, %d skipped, %d total." % (
            files_imported, files_skipped, files_imported + files_skipped)
        print
                        
        transaction.commit()
        transaction.leave_transaction_management()

