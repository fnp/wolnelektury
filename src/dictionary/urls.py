# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url
from dictionary.views import NotesView

urlpatterns = [
    url(r'^$', NotesView.as_view(), name='dictionary_notes'),
]
