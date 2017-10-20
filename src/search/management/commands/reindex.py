# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import sys
import traceback

from django.core.management.base import BaseCommand

from optparse import make_option


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


class Command(BaseCommand):
    help = 'Reindex everything.'
    args = ''
    
    option_list = BaseCommand.option_list + (
        make_option('-n', '--book-id', action='store_true', dest='book_id', default=False,
                    help='book id instead of slugs'),
        make_option('-t', '--just-tags', action='store_true', dest='just_tags', default=False,
                    help='just reindex tags'),
        make_option('--start', dest='start_from', default=None, help='start from this slug'),
        make_option('--stop', dest='stop_after', default=None, help='stop after this slug'),
    )

    def handle(self, *args, **opts):
        from catalogue.models import Book
        from search.index import Index
        idx = Index()
        
        if not opts['just_tags']:
            if args:
                books = []
                for a in args:
                    if opts['book_id']:
                        books += Book.objects.filter(id=int(a)).all()
                    else:
                        books += Book.objects.filter(slug=a).all()
            else:
                books = list(Book.objects.order_by('slug'))
            start_from = opts.get('start_from')
            stop_after = opts.get('stop_after')
            if start_from:
                start_from = start_from.replace('-', '')
            if stop_after:
                stop_after = stop_after.replace('-', '')
            while books:
                try:
                    b = books[0]
                    slug = b.slug.replace('-', '')
                    if stop_after and slug > stop_after:
                        break
                    if not start_from or slug >= start_from:
                        print b.slug
                        idx.index_book(b)
                        idx.index.commit()
                    books.pop(0)
                except:
                    traceback.print_exc()
                    try:
                        # we might not be able to rollback
                        idx.index.rollback()
                    except:
                        pass
                    retry = query_yes_no("Retry?")
                    if not retry:
                        break

        print 'Reindexing tags.'
        idx.index_tags()
        idx.index.commit()
