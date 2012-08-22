# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from optparse import make_option
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from catalogue import app_settings


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
        not_redakcja = []
        bad_license = defaultdict(list)
        no_license = []

        re_license = re.compile(ur'.*,\s*(CC.*)')

        redakcja_url = app_settings.REDAKCJA_URL
        good_license = re.compile("(%s)" % ")|(".join(
                            app_settings.GOOD_LICENSES))

        with transaction.commit_on_success():
            for book in Book.objects.all().order_by('slug').iterator():
                extra_info = book.extra_info
                if not extra_info.get('cover_url'):
                    if ancestor_has_cover(book):
                        with_ancestral_cover.append(book)
                    else:
                        without_cover.append(book)
                else:
                    if not extra_info.get('cover_source', ''
                                ).startswith(redakcja_url):
                        not_redakcja.append(book)
                    match = re_license.match(extra_info.get('cover_by', ''))
                    if match:
                        if not good_license.match(match.group(1)):
                            bad_license[match.group(1)].append(book)
                    else:
                        no_license.append(book)

        print """%d books with no covers, %d with inherited covers.
Bad licenses used: %s (%d covers without license).
%d covers not from %s.
""" % (
            len(without_cover),
            len(with_ancestral_cover),
            ", ".join(sorted(bad_license.keys())) or "none",
            len(no_license),
            len(not_redakcja),
            redakcja_url,
            )

        if verbose:
            if bad_license:
                print
                print "Bad license:"
                print "============"
                for lic, books in bad_license.items():
                    print
                    print lic
                    for book in books:
                        print full_url(book)

            if no_license:
                print
                print "No license:"
                print "==========="
                for book in no_license:
                    print
                    print full_url(book)
                    print book.extra_info.get('cover_by')
                    print book.extra_info.get('cover_source')
                    print book.extra_info.get('cover_url')

            if not_redakcja:
                print
                print "Not from Redakcja or source missing:"
                print "===================================="
                for book in not_redakcja:
                    print
                    print full_url(book)
                    print book.extra_info.get('cover_by')
                    print book.extra_info.get('cover_source')
                    print book.extra_info.get('cover_url')

            if without_cover:
                print
                print "No cover:"
                print "========="
                for book in without_cover:
                    print full_url(book)

            if with_ancestral_cover:
                print
                print "With ancestral cover:"
                print "====================="
                for book in with_ancestral_cover:
                    print full_url(book)
