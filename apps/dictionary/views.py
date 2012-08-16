# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from dictionary.models import Note
from django.views.generic.list import ListView


class NotesView(ListView):
    def get_queryset(self):
        self.letters = ["0-9"] + [chr(a) for a in range(ord('a'), ord('z')+1)]
        self.letter = self.kwargs.get('letter')

        objects = Note.objects.all()
        if self.letter == "0-9":
            objects = objects.filter(sort_key__regex=r"^[0-9]")
        elif self.letter:
            objects = objects.filter(sort_key__startswith=self.letter)
        return objects

    def get_context_data(self, **kwargs):
        context = super(NotesView, self).get_context_data(**kwargs)
        context['letter'] = self.letter
        context['letters'] = self.letters
        return context
