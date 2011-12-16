# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls.defaults import *


urlpatterns = patterns('infopages.views',
    url(r'^(?P<slug>[a-zA-Z0-9_-]+)/$', 'infopage', name='infopage'),
)

