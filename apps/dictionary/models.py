# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models, transaction
from celery.task import task
from sortify import sortify
from celery.utils.log import get_task_logger

task_logger = get_task_logger(__name__)

from catalogue.models import Book


class Qualifier(models.Model):
    qualifier = models.CharField(max_length=128, db_index=True, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ['qualifier']

    def __unicode__(self):
        return self.name or self.qualifier


class Note(models.Model):
    """Represents a single annotation from a book."""
    html = models.TextField()
    sort_key = models.CharField(max_length=128, db_index=True)
    fn_type = models.CharField(max_length=10, db_index=True)
    qualifiers = models.ManyToManyField(Qualifier)
    language = models.CharField(max_length=10, db_index=True)

    class Meta:
        ordering = ['sort_key']


class NoteSource(models.Model):
    """Represents a single annotation from a book."""
    note = models.ForeignKey(Note)
    book = models.ForeignKey(Book)
    anchor = models.CharField(max_length=64)

    class Meta:
        ordering = ['book']


@task(ignore_result=True)
def build_notes(book):
    task_logger.info(book.slug)
    with transaction.atomic():
        book.notesource_set.all().delete()
        if book.html_file:
            from librarian import html
            from librarian.fn_qualifiers import FN_QUALIFIERS

            for anchor, fn_type, qualifiers, text_str, html_str in \
                    html.extract_annotations(book.html_file.path):
                sort_key = sortify(text_str).strip()[:128]

                language = book.language
                note = None
                notes = Note.objects.filter(sort_key=sort_key,
                    fn_type=fn_type,
                    language=language, html=html_str)
                if notes:
                    note = notes[0]
                else:
                    note = Note.objects.create(
                        sort_key=sort_key,
                        html=html_str,
                        fn_type=fn_type,
                        language=language
                        )

                qualifier_objects = []
                for qualifier in qualifiers:
                    obj, created = Qualifier.objects.get_or_create(
                        qualifier=qualifier, defaults={
                            'name': FN_QUALIFIERS.get(qualifier, '')
                        })
                    qualifier_objects.append(obj)
                note.qualifiers = qualifier_objects
                note.notesource_set.create(book=book, anchor=anchor)

        Note.objects.filter(notesource=None).delete()


def notes_from_book(sender, instance, **kwargs):
    build_notes.delay(instance)
Book.html_built.connect(notes_from_book)
