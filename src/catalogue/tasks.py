# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from traceback import print_exc
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.utils import timezone

from catalogue.models import Book
from catalogue.utils import absolute_url, gallery_url
from waiter.models import WaitedFile

task_logger = get_task_logger(__name__)


# TODO: move to model?
def touch_tag(tag):
    update_dict = {
        'changed_at': timezone.now(),
    }

    type(tag).objects.filter(pk=tag.pk).update(**update_dict)


@shared_task(ignore_result=True)
def build_field(pk, field_name):
    book = Book.objects.get(pk=pk)
    task_logger.info("build %s.%s" % (book.slug, field_name))
    field_file = getattr(book, field_name)
    field_file.build()


@shared_task
def index_book(book_id, book_info=None, **kwargs):
    try:
        return Book.objects.get(id=book_id).search_index(book_info, **kwargs)
    except Exception as e:
        print("Exception during index: %s" % e)
        print_exc()
        raise e


@shared_task(ignore_result=True, rate_limit=settings.CATALOGUE_CUSTOMPDF_RATE_LIMIT)
def build_custom_pdf(book_id, customizations, file_name, waiter_id=None):
    """Builds a custom PDF file."""
    try:
        from django.core.files import File
        from django.core.files.storage import DefaultStorage

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
                base_url=absolute_url(gallery_url(wldoc.book_info.url.slug)),
                **kwargs)
            with open(pdf.get_filename(), 'rb') as f:
                DefaultStorage().save(file_name, File(f))
    finally:
        if waiter_id is not None:
            WaitedFile.objects.filter(pk=waiter_id).delete()


@shared_task(ignore_result=True)
def update_counters():
    from .helpers import update_counters
    update_counters()


@shared_task(ignore_result=True)
def update_references(book_id):
    Book.objects.get(id=book_id).update_references()

