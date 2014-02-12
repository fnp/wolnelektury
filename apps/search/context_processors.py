# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.core.urlresolvers import reverse
from search.forms import SearchForm


def search_form(request):
    return { 'search_form': SearchForm(reverse('search.views.hint'), request.GET) }
