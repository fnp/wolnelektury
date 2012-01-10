# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators import cache
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponsePermanentRedirect
from django.utils.translation import ugettext as _

from catalogue.utils import get_random_hash
from catalogue.models import Book, Tag, Fragment
from catalogue.fields import dumps
from catalogue.views import JSONResponse
from search import Search, JVM, SearchResult
from lucene import StringReader
from suggest.forms import PublishingSuggestForm

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


def hint(request):
    prefix = request.GET.get('term', '')
    if len(prefix) < 2:
        return JSONResponse([])
    JVM.attachCurrentThread()
    s = Search()

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
          'category': _(t.category),
          'id': t.id,
          'url': t.get_absolute_url()}
          for t in tags] + \
          [{'label': b.title,
            'category': _('book'),
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
    srch = Search()

    results = None
    query = None
    fuzzy = False

    if 'q' in request.GET:
        tags = request.GET.get('tags', '')
        query = request.GET['q']
        book_id = request.GET.get('book', None)
        book = None
        if book_id is not None:
            book = get_object_or_404(Book, id=book_id)

        hint = srch.hint()
        try:
            tag_list = Tag.get_tag_list(tags)
        except:
            tag_list = []

        if len(query) < 2:
            return render_to_response('catalogue/search_too_short.html', {'tags': tag_list, 'prefix': query},
                                      context_instance=RequestContext(request))

        hint.tags(tag_list)
        if book:
            hint.books(book)

        toks = StringReader(query)
        fuzzy = 'fuzzy' in request.GET
        if fuzzy:
            fuzzy = 0.7

        results = SearchResult.aggregate(srch.search_perfect_book(toks, fuzzy=fuzzy, hint=hint),
                                         srch.search_book(toks, fuzzy=fuzzy, hint=hint),
                                         srch.search_perfect_parts(toks, fuzzy=fuzzy, hint=hint),
                                         srch.search_everywhere(toks, fuzzy=fuzzy, hint=hint))

        for r in results:
            r.process_hits()

        results.sort(reverse=True)

        for r in results:
            print "-----"
            for h in r.hits:
                print "- %s" % h

        if len(results) == 1:
            if len(results[0].hits) == 0:
                return HttpResponseRedirect(results[0].book.get_absolute_url())
            elif len(results[0].hits) == 1 and results[0].hits[0] is not None:
                frag = Fragment.objects.get(anchor=results[0].hits[0])
                return HttpResponseRedirect(frag.get_absolute_url())
        elif len(results) == 0:
            form = PublishingSuggestForm(initial={"books": query + ", "})
            return render_to_response('catalogue/search_no_hits.html',
                                      {'tags': tag_list, 'prefix': query,
                                       "form": form},
                context_instance=RequestContext(request))

        return render_to_response('catalogue/search_multiple_hits.html',
                                  {'tags': tag_list, 'prefix': query,
                                   'results': results},
            context_instance=RequestContext(request))

    # return render_to_response('newsearch/search.html', {'results': results,
    #                                                     'did_you_mean': (query is not None) and
    #                                                     did_you_mean(query, srch.get_tokens(query, field='SIMPLE')),
    #                                                     'fuzzy': fuzzy},
    #                           context_instance=RequestContext(request))
