# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from optparse import make_option
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


def ancestor_has_cover(book):
    while book.parent:
        book = book.parent
        if book.extra_info.get('cover_url'):
            return True
    return False


current_domain = Site.objects.get_current().domain
def full_url(obj):
    return 'http://%s%s' % (
                current_domain,
                obj.get_absolute_url())


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-q', '--quiet', action='store_false', dest='verbose', default=True,
            help='Suppress output'),
    )
    help = 'Checks cover sources and licenses.'

    def handle(self, **options):
        from collections import defaultdict
        import re
        from django.db import transaction
        from catalogue.models import Book

        verbose = options['verbose']

        without_cover = []
        with_ancestral_cover = []
        by_flickr_author = defaultdict(list)
        not_flickr = []
        by_license = defaultdict(list)
        no_license = []

        re_flickr = re.compile(ur'https?://(?:www\.|secure\.)?flickr.com/photos/([^/]*)/.*')
        re_license = re.compile(ur'.*,\s*(CC.*)')

        with transaction.commit_on_success():
            for book in Book.objects.all().order_by('slug').iterator():
                extra_info = book.extra_info
                if not extra_info.get('cover_url'):
                    if ancestor_has_cover(book):
                        with_ancestral_cover.append(book)
                    else:
                        without_cover.append(book)
                else:
                    match = re_flickr.match(extra_info.get('cover_source', ''))
                    if match:
                        by_flickr_author[match.group(1)].append(book)
                    else:
                        not_flickr.append(book)
                    match = re_license.match(extra_info.get('cover_by', ''))
                    if match:
                        by_license[match.group(1)].append(book)
                    else:
                        no_license.append(book)

        print """%d books with no covers, %d with ancestral covers.
Licenses used: %s (%d covers without license).
Flickr authors: %s (%d covers not from flickr).
""" % (
            len(without_cover),
            len(with_ancestral_cover),
            ", ".join(sorted(by_license.keys())),
            len(no_license),
            ", ".join(sorted(by_flickr_author.keys())),
            len(not_flickr),
            )

        if verbose:
            print
            print "By license:"
            print "==========="
            for lic, books in by_license.items():
                print
                print lic
                for book in books:
                    print full_url(book)

            print
            print "No license:"
            print "==========="
            for book in no_license:
                print
                print full_url(book)
                print book.extra_info.get('cover_by')
                print book.extra_info.get('cover_source')
                print book.extra_info.get('cover_url')

            print
            print "By Flickr author:"
            print "================="
            for author, books in by_flickr_author.items():
                print
                print "author: http://flickr.com/photos/%s/" % author
                for book in books:
                    print full_url(book)

            print
            print "Not from Flickr or source missing:"
            print "=================================="
            for book in not_flickr:
                print
                print full_url(book)
                print book.extra_info.get('cover_by')
                print book.extra_info.get('cover_source')
                print book.extra_info.get('cover_url')

            print
            print "No cover:"
            print "========="
            for book in without_cover:
                print full_url(book)

            print
            print "With ancestral cover:"
            print "====================="
            for book in with_ancestral_cover:
                print full_url(book)
