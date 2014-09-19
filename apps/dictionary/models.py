# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from celery.task import task
from sortify import sortify

from catalogue.models import Book


class Note(models.Model):
    """Represents a single annotation from a book."""
    book = models.ForeignKey(Book)
    anchor = models.CharField(max_length=64)
    html = models.TextField()
    sort_key = models.CharField(max_length=128, db_index=True)

    class Meta:
        ordering = ['sort_key']


@task(ignore_result=True)
def build_notes(book):
    Note.objects.filter(book=book).delete()
    if book.html_file:
        from librarian import html
        for anchor, text_str, html_str in html.extract_annotations(book.html_file.path):
            Note.objects.create(book=book, anchor=anchor,
                               html=html_str,
                               sort_key=sortify(text_str).strip()[:128])

def notes_from_book(sender, instance, **kwargs):
    build_notes.delay(instance)
Book.html_built.connect(notes_from_book)
