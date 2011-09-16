# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls.defaults import *
from dictionary.models import Note


all_notes = Note.objects.all()

urlpatterns = patterns('django.views.generic.list_detail',
    url(r'^$', 'object_list', {'queryset': all_notes}),
)

