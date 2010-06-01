# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from suggest.forms import SuggestForm

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.direct_to_template', 
        {'template': 'suggest.html', 'extra_context': {'form': SuggestForm }}, name='suggest'),
    url(r'^wyslij/$', 'suggest.views.report', name='report'),
)

