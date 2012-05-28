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


@task
def index_book(book_id, book_info=None):
    from catalogue.models import Book
    try:
        return Book.objects.get(id=book_id).search_index(book_info)
    except Exception, e:
        print "Exception during index: %s" % e
        print_exc()
        raise e


@task(ignore_result=True)
def build_txt(book_id):
    """(Re)builds the TXT file for a book."""
    from django.core.files.base import ContentFile
    from catalogue.models import Book

    text = Book.objects.get(pk=book_id).wldocument().as_text()

    # Save the file in new instance. Building TXT takes time and we don't want
    # to overwrite any interim changes.
    book = Book.objects.get(id=book_id)
    book.txt_file.save('%s.txt' % book.slug, ContentFile(text.get_string()))


@task(ignore_result=True, rate_limit=settings.CATALOGUE_PDF_RATE_LIMIT)
def build_pdf(book_id):
    """(Re)builds the pdf file for a book."""
    from django.core.files import File
    from catalogue.models import Book
    from catalogue.utils import remove_zip
    from waiter.utils import clear_cache

    pdf = Book.objects.get(pk=book_id).wldocument().as_pdf(
            morefloats=settings.LIBRARIAN_PDF_MOREFLOATS)

    # Save the file in new instance. Building PDF takes time and we don't want
    # to overwrite any interim changes.
    book = Book.objects.get(id=book_id)
    book.pdf_file.save('%s.pdf' % book.slug,
             File(open(pdf.get_filename())))

    # Remove cached downloadables
    remove_zip(settings.ALL_PDF_ZIP)
    clear_cache(book.slug)


@task(ignore_result=True, rate_limit=settings.CATALOGUE_EPUB_RATE_LIMIT)
def build_epub(book_id):
    """(Re)builds the EPUB file for a book."""
    from django.core.files import File
    from catalogue.models import Book
    from catalogue.utils import remove_zip

    epub = Book.objects.get(pk=book_id).wldocument().as_epub()
    # Save the file in new instance. Building EPUB takes time and we don't want
    # to overwrite any interim changes.
    book = Book.objects.get(id=book_id)
    book.epub_file.save('%s.epub' % book.slug,
             File(open(epub.get_filename())))

    # remove zip with all epub files
    remove_zip(settings.ALL_EPUB_ZIP)


@task(ignore_result=True, rate_limit=settings.CATALOGUE_MOBI_RATE_LIMIT)
def build_mobi(book_id):
    """(Re)builds the MOBI file for a book."""
    from django.core.files import File
    from catalogue.models import Book
    from catalogue.utils import remove_zip

    mobi = Book.objects.get(pk=book_id).wldocument().as_mobi()
    # Save the file in new instance. Building MOBI takes time and we don't want
    # to overwrite any interim changes.
    book = Book.objects.get(id=book_id)
    book.mobi_file.save('%s.mobi' % book.slug,
             File(open(mobi.get_filename())))

    # remove zip with all mobi files
    remove_zip(settings.ALL_MOBI_ZIP)


@task(ignore_result=True, rate_limit=settings.CATALOGUE_MOBI_RATE_LIMIT)
def build_fb2(book_id, *args, **kwargs):
    """(Re)builds the MOBI file for a book."""
    from django.core.files import File
    from catalogue.models import Book
    from catalogue.utils import remove_zip

    fb2 = Book.objects.get(pk=book_id).wldocument().as_fb2()
    # Save the file in new instance. Building FB2 takes time and we don't want
    # to overwrite any interim changes.
    book = Book.objects.get(id=book_id)
    book.fb2_file.save('%s.fb2' % book.slug,
             File(open(fb2.get_filename())))

    # remove zip with all mobi files
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
