# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from dictionary.views import NotesView

urlpatterns = [
    path('', NotesView.as_view(), name='dictionary_notes'),
]
