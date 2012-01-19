
from django.core.urlresolvers import reverse
from search.forms import SearchForm


def search_form(request):
    return { 'search_form': SearchForm(reverse('search.views.hint'), request.GET) }
