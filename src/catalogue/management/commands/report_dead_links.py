# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from __future__ import print_function, unicode_literals

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Checks for dead links.'

    def handle(self, **options):
        from catalogue.models import Book
        from picture.models import Picture
        from urllib2 import urlopen, HTTPError, URLError
        from django.core.urlresolvers import reverse
        from django.contrib.sites.models import Site

        domain = Site.objects.get_current().domain

        fields = [
            (
                Book,
                [
                    ('wiki_link', lambda b: b.wiki_link),
                    ('źródło', lambda b: b.extra_info.get('source_url')),
                ],
                'admin:catalogue_book_change'
            ),
            (
                Picture,
                [
                    ('wiki_link', lambda p: p.wiki_link),
                    ('źródło', lambda p: p.extra_info.get('source_url')),
                ],
                'admin:pictures_picture_change'
            )
        ]

        for model, model_fields, admin_name in fields:
            for obj in model.objects.all():
                clean = True
                for name, get in model_fields:
                    url = get(obj)
                    if url:
                        try:
                            urlopen(url)
                        except (HTTPError, URLError, ValueError), e:
                            if clean:
                                clean = False
                                print(unicode(obj).encode('utf-8'))
                                print(('Na stronie: https://%s%s' % (domain, obj.get_absolute_url())).encode('utf-8'))
                                print(
                                    ('Administracja: https://%s%s' % (domain, reverse(admin_name, args=[obj.pk])))
                                    .encode('utf-8'))
                                if obj.extra_info.get('about'):
                                    print(('Redakcja: %s' % (obj.extra_info.get('about'),)).encode('utf-8'))
                            print(('    %s (%s): %s' % (name, getattr(e, 'code', 'błąd'), url)).encode('utf-8'))
                if not clean:
                    print()
