# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import datetime
from traceback import print_exc
from celery.task import task
from django.conf import settings


# TODO: move to model?
def touch_tag(tag):
    update_dict = {
        'book_count': tag.get_count(),
        'changed_at': datetime.now(),
    }

    type(tag).objects.filter(pk=tag.pk).update(**update_dict)


@task(ignore_result=True)
def fix_tree_tags(book):
    book.fix_tree_tags()


@task
def index_book(book_id, book_info=None):
    from catalogue.models import Book
    try:
        return Book.objects.get(id=book_id).search_index(book_info)
    except Exception, e:
        print "Exception during index: %s" % e
        print_exc()
        raise e


@task(ignore_result=True, rate_limit=settings.CATALOGUE_CUSTOMPDF_RATE_LIMIT)
def build_custom_pdf(book_id, customizations, file_name):
    """Builds a custom PDF file."""
    from django.core.files import File
    from django.core.files.storage import DefaultStorage
    from catalogue.models import Book

    print "will gen %s" % DefaultStorage().path(file_name)
    if not DefaultStorage().exists(file_name):
        pdf = Book.objects.get(pk=book_id).wldocument().as_pdf(
                customizations=customizations,
                morefloats=settings.LIBRARIAN_PDF_MOREFLOATS)
        DefaultStorage().save(file_name, File(open(pdf.get_filename())))
