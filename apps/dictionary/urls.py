# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls.defaults import *


urlpatterns = patterns('dictionary.views',
    url(r'^$', 'letter_notes', name='dictionary_notes'),
    url(r'(?P<letter>[a-z]|0-9)/$', 'letter_notes', name='dictionary_notes'),
)

