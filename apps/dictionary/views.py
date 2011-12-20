# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.views.generic.list_detail import object_list
from catalogue.forms import SearchForm
from dictionary.models import Note

def letter_notes(request, letter=None):
    letters = ["0-9"] + [chr(a) for a in range(ord('a'), ord('z')+1)]
    objects = Note.objects.all()
    if letter == "0-9":
        objects = objects.filter(sort_key__regex=r"^[0-9]")
    elif letter:
        objects = objects.filter(sort_key__startswith=letter)

    return object_list(request, queryset=objects, extra_context=locals())
