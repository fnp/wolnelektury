# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import datetime
from traceback import print_exc
from celery.task import task
from django.conf import settings
from wolnelektury.utils import localtime_to_utc
from waiter.models import WaitedFile


# TODO: move to model?
def touch_tag(tag):
    update_dict = {
        'changed_at': localtime_to_utc(datetime.now()),
    }

    type(tag).objects.filter(pk=tag.pk).update(**update_dict)


@task
def index_book(book_id, book_info=None, **kwargs):
    from catalogue.models import Book
    try:
        return Book.objects.get(id=book_id).search_index(book_info, **kwargs)
    except Exception, e:
        print "Exception during index: %s" % e
        print_exc()
        raise e


@task(ignore_result=True, rate_limit=settings.CATALOGUE_CUSTOMPDF_RATE_LIMIT)
def build_custom_pdf(book_id, customizations, file_name, waiter_id=None):
    """Builds a custom PDF file."""
    try:
        from django.core.files import File
        from django.core.files.storage import DefaultStorage
        from catalogue.models import Book

        print "will gen %s" % DefaultStorage().path(file_name)
        if not DefaultStorage().exists(file_name):
            kwargs = {
                'cover': True,
            }
            if 'no-cover' in customizations:
                kwargs['cover'] = False
                customizations.remove('no-cover')
            pdf = Book.objects.get(pk=book_id).wldocument().as_pdf(
                    customizations=customizations,
                    morefloats=settings.LIBRARIAN_PDF_MOREFLOATS,
                    **kwargs)
            DefaultStorage().save(file_name, File(open(pdf.get_filename())))
    finally:
        if waiter_id is not None:
            WaitedFile.objects.filter(pk=waiter_id).delete()
