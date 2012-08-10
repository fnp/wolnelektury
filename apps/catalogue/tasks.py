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


def _build_ebook(book_id, ext, transform):
    """Generic ebook builder."""
    from django.core.files import File
    from catalogue.models import Book

    book = Book.objects.get(pk=book_id)
    out = transform(book.wldocument())
    field_name = '%s_file' % ext
    # Update instead of saving the model to avoid race condition.
    getattr(book, field_name).save('%s.%s' % (book.slug, ext),
            File(open(out.get_filename())),
            save=False
        )
    Book.objects.filter(pk=book_id).update(**{
            field_name: getattr(book, field_name)
        })


@task(ignore_result=True)
def build_txt(book_id):
    """(Re)builds the TXT file for a book."""
    _build_ebook(book_id, 'txt', lambda doc: doc.as_text())


@task(ignore_result=True, rate_limit=settings.CATALOGUE_PDF_RATE_LIMIT)
def build_pdf(book_id):
    """(Re)builds the pdf file for a book."""
    from catalogue.models import Book
    from catalogue.utils import remove_zip
    from waiter.utils import clear_cache

    _build_ebook(book_id, 'pdf',
        lambda doc: doc.as_pdf(morefloats=settings.LIBRARIAN_PDF_MOREFLOATS))
    # Remove cached downloadables
    remove_zip(settings.ALL_PDF_ZIP)
    book = Book.objects.get(pk=book_id)
    clear_cache(book.slug)


@task(ignore_result=True, rate_limit=settings.CATALOGUE_EPUB_RATE_LIMIT)
def build_epub(book_id):
    """(Re)builds the EPUB file for a book."""
    from catalogue.utils import remove_zip

    _build_ebook(book_id, 'epub', lambda doc: doc.as_epub())
    # remove zip with all epub files
    remove_zip(settings.ALL_EPUB_ZIP)


@task(ignore_result=True, rate_limit=settings.CATALOGUE_MOBI_RATE_LIMIT)
def build_mobi(book_id):
    """(Re)builds the MOBI file for a book."""
    from catalogue.utils import remove_zip

    _build_ebook(book_id, 'mobi', lambda doc: doc.as_mobi())
    # remove zip with all mobi files
    remove_zip(settings.ALL_MOBI_ZIP)


@task(ignore_result=True, rate_limit=settings.CATALOGUE_FB2_RATE_LIMIT)
def build_fb2(book_id, *args, **kwargs):
    """(Re)builds the FB2 file for a book."""
    from catalogue.utils import remove_zip

    _build_ebook(book_id, 'fb2', lambda doc: doc.as_fb2())
    # remove zip with all fb2 files
    remove_zip(settings.ALL_FB2_ZIP)


@task(rate_limit=settings.CATALOGUE_CUSTOMPDF_RATE_LIMIT)
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
