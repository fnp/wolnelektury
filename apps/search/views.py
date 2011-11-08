

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators import cache

from catalogue.utils import get_random_hash
from catalogue.models import Book, Tag
from catalogue import forms
from search import MultiSearch, JVM, SearchResult


def main(request):
    results = {}
    JVM.attachCurrentThread()  # where to put this?
    srch = MultiSearch()

    results = None
    if 'q' in request.GET:
        toks = srch.get_tokens(request.GET['q'])
        results = SearchResult.aggregate(srch.search_perfect_book(toks),
                                         srch.search_perfect_parts(toks),
                                         srch.search_everywhere(toks))
        results.sort(reverse=True)

        for r in results:
            print r.parts

    return render_to_response('newsearch/search.html', {"results": results},
                              context_instance=RequestContext(request))
