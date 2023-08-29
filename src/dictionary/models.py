# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import models, transaction
from celery import shared_task
from sortify import sortify
from celery.utils.log import get_task_logger

from catalogue.models import Book

task_logger = get_task_logger(__name__)


class Qualifier(models.Model):
    qualifier = models.CharField(max_length=128, db_index=True, unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ['qualifier']

    def __str__(self):
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
    note = models.ForeignKey(Note, models.CASCADE)
    book = models.ForeignKey(Book, models.CASCADE)
    anchor = models.CharField(max_length=64)

    class Meta:
        ordering = ['book']


@shared_task(ignore_result=True)
def build_notes(book):
    if not book.findable:
        return
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
                notes = Note.objects.filter(sort_key=sort_key, fn_type=fn_type, language=language, html=html_str)
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
                note.qualifiers.set(qualifier_objects)
                note.notesource_set.create(book=book, anchor=anchor)

        Note.objects.filter(notesource=None).delete()


def notes_from_book(sender, instance, **kwargs):
    if instance.findable:
        build_notes.delay(instance)
Book.html_built.connect(notes_from_book)
