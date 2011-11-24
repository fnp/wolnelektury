# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators import cache

from catalogue.utils import get_random_hash
from catalogue.models import Book, Tag, TAG_CATEGORIES
from catalogue.fields import dumps
from catalogue.views import JSONResponse
from catalogue import forms
from search import MultiSearch, JVM, SearchResult
from lucene import StringReader

import enchant

dictionary = enchant.Dict('pl_PL')


def did_you_mean(query, tokens):
    change = {}
    # sprawdzić, czy słowo nie jest aby autorem - proste szukanie termu w author!
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


def category_name(category):
    try:
        return filter(lambda c: c[0] == category, TAG_CATEGORIES)[0][1].encode('utf-8')
    except IndexError:
        raise KeyError("No category %s" % category)


def hint(request):
    prefix = request.GET.get('term', '')
    if len(prefix) < 2:
        return JSONResponse(dumps(None))
    JVM.attachCurrentThread()
    s = MultiSearch()

    hint = s.hint()
    try:
        tags = request.GET.get('tags', '')
        hint.tags(Tag.get_tag_list(tags))
    except:
        pass

    # tagi beda ograniczac tutaj
    # ale tagi moga byc na ksiazce i na fragmentach
    # jezeli tagi dot tylko ksiazki, to wazne zeby te nowe byly w tej samej ksiazce
    # jesli zas dotycza themes, to wazne, zeby byly w tym samym fragmencie.

    tags = s.hint_tags(prefix)
    books = s.hint_books(prefix)

    # TODO DODAC TU HINTY

    return JSONResponse(
        [{'label': t.name,
          'category': category_name(t.category),
          'id': t.id,
          'url': t.get_absolute_url()}
          for t in tags] + \
          [{'label': b.title,
            'category': category_name('book'),
            'id': b.id,
            'url': b.get_absolute_url()}
            for b in books])


def foo(s, q, tag_list=None):
    hint = s.hint()
    try:
        tag_list = Tag.get_tag_list(tag_list)
        hint.tags(tag_list)
    except:
        tag_list = None

    q = StringReader(q)
    return (q, hint)


def main(request):
    results = {}
    JVM.attachCurrentThread()  # where to put this?
    srch = MultiSearch()

    results = None
    query = None
    fuzzy = False

    if 'q' in request.GET:
        tags = request.GET.get('tags', '')
        hint = srch.hint()
        try:
            tag_list = Tag.get_tag_list(tags)
        except:
            tag_list = []

        hint.tags(tag_list)

        query = request.GET['q']
        toks = StringReader(query)
        fuzzy = 'fuzzy' in request.GET
        if fuzzy:
            fuzzy = 0.7

        results = SearchResult.aggregate(srch.search_perfect_book(toks, fuzzy=fuzzy, hint=hint),
                                         srch.search_perfect_parts(toks, fuzzy=fuzzy, hint=hint),
                                         srch.search_everywhere(toks, fuzzy=fuzzy, hint=hint))
        results.sort(reverse=True)

        for r in results:
            print r.hits

    return render_to_response('newsearch/search.html', {'results': results,
                                                        'did_you_mean': (query is not None) and
                                                        did_you_mean(query, srch.get_tokens(query, field='SIMPLE')),
                                                        'fuzzy': fuzzy},
                              context_instance=RequestContext(request))
