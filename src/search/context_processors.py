# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import reverse
from search.forms import SearchForm


def search_form(request):
    return {'search_form': SearchForm(reverse('search_hint') + '?max=10', request.GET)}
