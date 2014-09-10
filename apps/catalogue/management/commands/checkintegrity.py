# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from optparse import make_option
from django.core.management.base import BaseCommand

from catalogue.models import Book


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-q', '--quiet', action='store_false', dest='verbose', default=True,
            help='Suppress output'),
        make_option('-d', '--dry-run', action='store_true', dest='dry_run', default=False,
            help="Just check for problems, don't fix them"),
    )
    help = 'Checks integrity of catalogue data.'

    def handle(self, **options):
        from django.db import transaction

        verbose = options['verbose']

        with transaction.commit_on_success():
            for book in Book.objects.all().iterator():
                try:
                    info = book.wldocument().book_info
                except:
                    if verbose:
                        print "ERROR! Bad XML for book:", book.slug
                        print "To resolve: republish."
                        print
                else:
                    should_be = [p.slug for p in info.parts]
                    is_now = [p.slug for p in book.children.all().order_by('parent_number')]
                    if should_be != is_now:
                        if verbose:
                            print "ERROR! Wrong children for book:", book.slug
                            print "Is:       ", is_now
                            print "Should be:", should_be
                            print "To resolve: republish parent book."
                            print

                # Check for ancestry.
                parents = []
                parent = book.parent
                while parent:
                    parents.append(parent)
                    parent = parent.parent
                ancestors = list(book.ancestor.all())
                if set(ancestors) != set(parents):
                    if options['verbose']:
                        print "Wrong ancestry for book:", book
                        print "Is:       ", ", ".join(ancestors)
                        print "Should be:", ", ".join(parents)
                    if not options['dry_run']:
                        book.fix_tree_tags()
                        if options['verbose']:
                            print "Fixed."
                    if options['verbose']:
                        print

                # TODO: check metadata tags, reset counters
