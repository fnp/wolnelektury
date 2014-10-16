# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from dictionary.models import Note
from django.views.generic.list import ListView
from django.db.models import Count


class NotesView(ListView):
    def get_queryset(self):
        self.letters = ["0-9"] + [chr(a) for a in range(ord('a'), ord('z')+1)]
        self.letter = self.request.GET.get('ltr')

        self.qualifiers = Note.objects.order_by('qualifier').filter(qualifier__startswith='f').values_list(
            'qualifier', flat=True).distinct()
        self.qualifier = self.request.GET.get('qual')

        self.languages = Note.objects.order_by('language').values_list(
            'language', flat=True).distinct()
        self.language = self.request.GET.get('lang')

        self.fn_types = Note.objects.order_by('fn_type').values_list(
            'fn_type', flat=True).distinct()
        self.fn_type = self.request.GET.get('type')

        objects = Note.objects.select_related('book').all()

        if self.letter == "0-9":
            objects = objects.filter(sort_key__regex=r"^[0-9]")
        elif self.letter:
            objects = objects.filter(sort_key__startswith=self.letter)

        if self.qualifier:
            objects = objects.filter(qualifier=self.qualifier)

        if self.language:
            objects = objects.filter(language=self.language)

        if self.fn_type:
            objects = objects.filter(fn_type=self.fn_type)

        return objects

        # TODO: wewn. wyszukiwarka, czy wg definiendum?
        # TODO: filtr języka

    def get_context_data(self, **kwargs):
        context = super(NotesView, self).get_context_data(**kwargs)
        context['letters'] = self.letters
        context['letter'] = self.letter
        context['qualifiers'] = self.qualifiers
        context['qualifier'] = self.qualifier
        context['languages'] = self.languages
        context['language'] = self.language
        context['fn_types'] = self.fn_types
        context['fn_type'] = self.fn_type
        return context
