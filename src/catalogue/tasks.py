# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from traceback import print_exc
from celery.task import task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.utils import timezone

from catalogue.utils import gallery_path
from waiter.models import WaitedFile

task_logger = get_task_logger(__name__)


# TODO: move to model?
def touch_tag(tag):
    update_dict = {
        'changed_at': timezone.now(),
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

        task_logger.info(DefaultStorage().path(file_name))
        if not DefaultStorage().exists(file_name):
            kwargs = {
                'cover': True,
            }
            if 'nocover' in customizations:
                kwargs['cover'] = False
                customizations.remove('nocover')
            wldoc = Book.objects.get(pk=book_id).wldocument()
            pdf = wldoc.as_pdf(
                customizations=customizations,
                morefloats=settings.LIBRARIAN_PDF_MOREFLOATS,
                ilustr_path=gallery_path(wldoc.book_info.url.slug),
                **kwargs)
            DefaultStorage().save(file_name, File(open(pdf.get_filename())))
    finally:
        if waiter_id is not None:
            WaitedFile.objects.filter(pk=waiter_id).delete()


@task(ignore_result=True)
def update_counters():
    from .helpers import update_counters
    update_counters()
