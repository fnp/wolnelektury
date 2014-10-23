# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from dictionary.models import Note, Qualifier
from django.views.generic.list import ListView
from django.db.models import Count, Q


class NotesView(ListView):
    def get_queryset(self):
        objects = Note.objects.select_related('book').all()
        filters = {}

        try:
            self.qualifier = Qualifier.objects.get(qualifier=self.request.GET.get('qual'))
        except Qualifier.DoesNotExist:
            self.qualifier = None
        else:
            filters['qualifier'] = Q(qualifiers=self.qualifier)

        self.language = self.request.GET.get('lang')
        if self.language:
            filters['language'] = Q(language=self.language)

        self.fn_type = self.request.GET.get('type')
        if self.fn_type:
            filters['fn_type'] = Q(fn_type=self.fn_type)

        self.letter = self.request.GET.get('ltr')
        if self.letter == "0-9":
            objects = objects.filter(sort_key__regex=r"^[0-9]")
            #filters['letter'] = Q(sort_key__regex=r"^[0-9]")
        elif self.letter:
            objects = objects.filter(sort_key__startswith=self.letter)
            #filters['letter'] = Q(sort_key__startswith=self.letter)

        self.letters = ["0-9"] + [chr(a) for a in range(ord('a'), ord('z')+1)]

        nobj = objects
        for key, fltr in filters.items():
            if key != 'qualifier':
                nobj = nobj.filter(fltr)
        self.qualifiers = Qualifier.objects.filter(note__in=nobj).distinct()

        nobj = objects
        for key, fltr in filters.items():
            if key != 'language':
                nobj = nobj.filter(fltr)
        self.languages = nobj.order_by('language').values_list(
            'language', flat=True).distinct()

        nobj = objects
        for key, fltr in filters.items():
            if key != 'fn_type':
                nobj = nobj.filter(fltr)
        self.fn_types = nobj.order_by('fn_type').values_list(
            'fn_type', flat=True).distinct()

        for f in filters.values():
            objects = objects.filter(f)

        return objects

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
