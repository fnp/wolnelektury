# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls.defaults import *
from catalogue import forms


urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.direct_to_template', {
        'template': 'lessons/document_list.html',
    }, name='lessons_document_list'),

    url(r'^(?P<slug>[a-zA-Z0-9_-]+)/$', 'lessons.views.document_detail', name='lessons_document_detail'),
)

