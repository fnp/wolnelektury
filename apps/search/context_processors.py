
from catalogue.forms import SearchForm
from django.core.urlresolvers import reverse


def search_form(request):
    return { 'search_form': SearchForm(reverse('search.views.hint'), request.GET) }
