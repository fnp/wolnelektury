# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import os.path

from django.core.management.base import BaseCommand
from django.core.files import File
from slughifi import slughifi

from catalogue.models import Book, BookMedia
from catalogue.utils import ExistingFile


class Command(BaseCommand):
    help = "Saves uploaded media with a given book and a given name. If media has a source SHA1 info - matching media is replaced."
    args = 'path slug name'

    def handle(self, *args, **options):
        from django.db import transaction

        path, slug, name = args

        # Start transaction management.
        transaction.commit_unless_managed()
        transaction.enter_transaction_management()
        transaction.managed(True)

        book = Book.objects.get(slug=slug)

        root, ext = os.path.splitext(path)
        ext = ext.lower()
        if ext:
            ext = ext[1:]
            if ext == 'zip':
                ext = 'daisy'

        source_sha1 = BookMedia.read_source_sha1(path, ext)
        print "Source file SHA1:", source_sha1
        try:
            assert source_sha1
            bm = book.media.get(type=ext, source_sha1=source_sha1)
            print "Replacing media: %s (%s)" % (bm.name, ext)
        except (AssertionError, BookMedia.DoesNotExist):
            bm = BookMedia(book=book, type=ext, name=name)
            print "Creating new media"
        bm.file.save(slughifi(name), ExistingFile(path))
        bm.save()
        transaction.commit()
        transaction.leave_transaction_management()
