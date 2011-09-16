# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models

from librarian import html
from sortify import sortify

from catalogue.models import Book


class Note(models.Model):
    book = models.ForeignKey(Book)
    anchor = models.CharField(max_length=64)
    html = models.TextField()
    sort_key = models.CharField(max_length=128, db_index=True)

    class Meta:
        ordering = ['sort_key']


def notes_from_book(sender, **kwargs):
    Note.objects.filter(book=sender).delete()
    if sender.has_html_file:
        for anchor, text_str, html_str in html.extract_annotations(sender.html_file.path):
            Note.objects.create(book=sender, anchor=anchor,
                               html=html_str, sort_key=sortify(text_str)[:128])

Book.html_built.connect(notes_from_book)
