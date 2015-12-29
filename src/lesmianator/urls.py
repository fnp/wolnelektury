# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url, patterns

urlpatterns = patterns('lesmianator.views',
    url(r'^$', 'main_page', name='lesmianator'),
    url(r'^wiersz/$', 'new_poem', name='new_poem'),
    url(r'^lektura/(?P<slug>[a-z0-9-]+)/$', 'poem_from_book', name='poem_from_book'),
    url(r'^polka/(?P<shelf>[a-zA-Z0-9-]+)/$', 'poem_from_set', name='poem_from_set'),
    url(r'^wiersz/(?P<poem>[a-zA-Z0-9-]+)/$', 'get_poem', name='get_poem'),
)

