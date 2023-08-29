# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.urls import path
from dictionary.views import NotesView

urlpatterns = [
    path('', NotesView.as_view(), name='dictionary_notes'),
]
