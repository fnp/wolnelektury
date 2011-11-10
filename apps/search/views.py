
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators import cache

from catalogue.utils import get_random_hash
from catalogue.models import Book, Tag
from catalogue import forms
from search import MultiSearch, JVM, SearchResult
from lucene import StringReader

import enchant

dictionary = enchant.Dict('pl_PL')


def did_you_mean(query, tokens):
    change = {}
    
    for t in tokens:
        print("%s ok? %s, sug: %s" %(t, dictionary.check(t), dictionary.suggest(t)))
        if not dictionary.check(t):
            try:
                change[t] = dictionary.suggest(t)[0]
            except IndexError:
                pass

    if change == {}:
        return None

    for frm, to in change.items():
        query = query.replace(frm, to)
        
    return query


def main(request):
    results = {}
    JVM.attachCurrentThread()  # where to put this?
    srch = MultiSearch()

    results = None
    query = None
    fuzzy = False
    if 'q' in request.GET:
        query = request.GET['q']
        toks = StringReader(query)
        fuzzy = 'fuzzy' in request.GET
        if fuzzy:
            fuzzy = 0.7


        results = SearchResult.aggregate(srch.search_perfect_book(toks, fuzzy=fuzzy),
                                         srch.search_perfect_parts(toks, fuzzy=fuzzy),
                                         srch.search_everywhere(toks, fuzzy=fuzzy))
        results.sort(reverse=True)

        for r in results:
            print r.parts

    return render_to_response('newsearch/search.html', {'results': results,
                                                        'did_you_mean': (query is not None) and 
                                                        did_you_mean(query, srch.get_tokens(query, field='SIMPLE')),
                                                        'fuzzy': fuzzy},
                              context_instance=RequestContext(request))
