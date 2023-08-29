# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.utils.functional import lazy
from catalogue import app_settings


def ancestor_has_cover(book):
    while book.parent:
        book = book.parent
        if book.get_extra_info_json().get('cover_url'):
            return True
    return False


current_domain = lazy(lambda: Site.objects.get_current().domain, str)()


def full_url(obj):
    return 'http://%s%s' % (
                current_domain,
                obj.get_absolute_url())


class Command(BaseCommand):
    help = 'Checks cover sources and licenses.'

    def add_arguments(self, parser):
        parser.add_argument(
                '-q', '--quiet', action='store_false', dest='verbose',
                default=True, help='Suppress output')

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

        re_license = re.compile(r'.*,\s*(CC.*)')

        redakcja_url = app_settings.REDAKCJA_URL
        good_license = re.compile("(%s)" % ")|(".join(
                            app_settings.GOOD_LICENSES))

        with transaction.atomic():
            for book in Book.objects.all().order_by('slug').iterator():
                extra_info = book.get_extra_info_json()
                if not extra_info.get('cover_url'):
                    if ancestor_has_cover(book):
                        with_ancestral_cover.append(book)
                    else:
                        without_cover.append(book)
                else:
                    if not extra_info.get('cover_source', '').startswith(redakcja_url):
                        not_redakcja.append(book)
                    match = re_license.match(extra_info.get('cover_by', ''))
                    if match:
                        if not good_license.match(match.group(1)):
                            bad_license[match.group(1)].append(book)
                    else:
                        no_license.append(book)

        print("""%d books with no covers, %d with inherited covers.
Bad licenses used: %s (%d covers without license).
%d covers not from %s.
""" % (
            len(without_cover),
            len(with_ancestral_cover),
            ", ".join(sorted(bad_license.keys())) or "none",
            len(no_license),
            len(not_redakcja),
            redakcja_url,
            ))

        if verbose:
            if bad_license:
                print()
                print("Bad license:")
                print("============")
                for lic, books in bad_license.items():
                    print()
                    print(lic)
                    for book in books:
                        print(full_url(book))

            if no_license:
                print()
                print("No license:")
                print("===========")
                for book in no_license:
                    print()
                    print(full_url(book))
                    extra_info = book.get_extra_info_json()
                    print(extra_info.get('cover_by'))
                    print(extra_info.get('cover_source'))
                    print(extra_info.get('cover_url'))

            if not_redakcja:
                print()
                print("Not from Redakcja or source missing:")
                print("====================================")
                for book in not_redakcja:
                    print()
                    print(full_url(book))
                    extra_info = book.get_extra_info_json()
                    print(extra_info.get('cover_by'))
                    print(extra_info.get('cover_source'))
                    print(extra_info.get('cover_url'))

            if without_cover:
                print()
                print("No cover:")
                print("=========")
                for book in without_cover:
                    print(full_url(book))

            if with_ancestral_cover:
                print()
                print("With ancestral cover:")
                print("=====================")
                for book in with_ancestral_cover:
                    print(full_url(book))
