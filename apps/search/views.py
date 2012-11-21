# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators import cache
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponsePermanentRedirect
from django.utils.translation import ugettext as _

from catalogue.utils import split_tags
from catalogue.models import Book, Tag, Fragment
from pdcounter.models import Author as PDCounterAuthor, BookStub as PDCounterBook
from catalogue.views import JSONResponse
from search import Search, SearchResult
from suggest.forms import PublishingSuggestForm
import re
#import enchant
import json


def match_word_re(word):
    if 'sqlite' in settings.DATABASES['default']['ENGINE']:
        return r"\b%s\b" % word
    elif 'mysql' in settings.DATABASES['default']['ENGINE']:
        return "[[:<:]]%s[[:>:]]" % word


query_syntax_chars = re.compile(r"[\\/*:(){}]")


def remove_query_syntax_chars(query, replace=' '):
    return query_syntax_chars.sub(' ', query)


def did_you_mean(query, tokens):
    return query
    # change = {}
    # for t in tokens:
    #     authors = Tag.objects.filter(category='author', name__iregex=match_word_re(t))
    #     if len(authors) > 0:
    #         continue

    #     if False:
    #         if not dictionary.check(t):
    #             try:
    #                 change_to = dictionary.suggest(t)[0].lower()
    #                 if change_to != t.lower():
    #                     change[t] = change_to
    #             except IndexError:
    #                 pass

    # if change == {}:
    #     return None

    # for frm, to in change.items():
    #     query = query.replace(frm, to)

    # return query


def hint(request):
    prefix = request.GET.get('term', '')
    if len(prefix) < 2:
        return JSONResponse([])

    prefix = remove_query_syntax_chars(prefix)

    search = Search()
    # tagi beda ograniczac tutaj
    # ale tagi moga byc na ksiazce i na fragmentach
    # jezeli tagi dot tylko ksiazki, to wazne zeby te nowe byly w tej samej ksiazce
    # jesli zas dotycza themes, to wazne, zeby byly w tym samym fragmencie.

    tags = search.hint_tags(prefix, pdcounter=True)
    books = search.hint_books(prefix)

    def is_dupe(tag):
        if isinstance(tag, PDCounterAuthor):
            if filter(lambda t: t.slug == tag.slug and t != tag, tags):
                return True
        elif isinstance(tag, PDCounterBook):
            if filter(lambda b: b.slug == tag.slug, tags):
                return True
        return False

    tags = filter(lambda t: not is_dupe(t), tags)

    def category_name(c):
        if c.startswith('pd_'):
            c = c[len('pd_'):]
        return _(c)

    callback = request.GET.get('callback', None)
    data = [{'label': t.name,
              'category': category_name(t.category),
              'id': t.id,
              'url': t.get_absolute_url()}
              for t in tags] + \
              [{'label': b.title,
                'category': _('book'),
                'id': b.id,
                'url': b.get_absolute_url()}
                for b in books]
    if callback:
        return HttpResponse("%s(%s);" % (callback, json.dumps(data)),
                            content_type="application/json; charset=utf-8")
    else:
        return JSONResponse(data)


def main(request):
    results = {}

    results = None
    query = None

    query = request.GET.get('q', '')

    if len(query) < 2:
        return render_to_response('catalogue/search_too_short.html',
                                  {'prefix': query},
            context_instance=RequestContext(request))

    query = remove_query_syntax_chars(query)
    
    search = Search()

    theme_terms = search.index.analyze(text=query, field="themes_pl") \
        + search.index.analyze(text=query, field="themes")

            # change hints
    tags = search.hint_tags(query, pdcounter=True, prefix=False)
    tags = split_tags(tags)

    author_results = search.search_phrase(query, 'authors', book=True)
    translator_results = search.search_phrase(query, 'translators', book=True)

    title_results = search.search_phrase(query, 'title', book=True)

    # Boost main author/title results with mixed search, and save some of its results for end of list.
    # boost author, title results
    author_title_mixed = search.search_some(query, ['authors', 'translators', 'title', 'tags'], query_terms=theme_terms)
    author_title_rest = []

    for b in author_title_mixed:
        also_in_mixed = filter(lambda ba: ba.book_id == b.book_id, author_results + translator_results + title_results)
        for b2 in also_in_mixed:
            b2.boost *= 1.1
        if also_in_mixed is []:
            author_title_rest.append(b)

    # Do a phrase search but a term search as well - this can give us better snippets then search_everywhere,
    # Because the query is using only one field.
    text_phrase = SearchResult.aggregate(
        search.search_phrase(query, 'text', snippets=True, book=False),
        search.search_some(query, ['text'], snippets=True, book=False, query_terms=theme_terms))

    everywhere = search.search_everywhere(query, query_terms=theme_terms)

    def already_found(results):
        def f(e):
            for r in results:
                if e.book_id == r.book_id:
                    e.boost = 0.9
                    results.append(e)
                    return True
            return False
        return f
    f = already_found(author_results + translator_results + title_results + text_phrase)
    everywhere = filter(lambda x: not f(x), everywhere)

    author_results = SearchResult.aggregate(author_results)
    translator_results = SearchResult.aggregate(translator_results)
    title_results = SearchResult.aggregate(title_results)

    everywhere = SearchResult.aggregate(everywhere, author_title_rest)

    for field, res in [('authors', author_results),
                       ('translators', translator_results),
                       ('title', title_results),
                       ('text', text_phrase),
                       ('text', everywhere)]:
        res.sort(reverse=True)
        for r in res:
            search.get_snippets(r, query, field, 3)

    suggestion = u''

    def ensure_exists(r):
        try:
            return r.book
        except Book.DoesNotExist:
            return False

    author_results = filter(ensure_exists, author_results)
    translator_results = filter(ensure_exists, translator_results)
    title_results = filter(ensure_exists, title_results)
    text_phrase = filter(ensure_exists, text_phrase)
    everywhere = filter(ensure_exists, everywhere)

    results = author_results + translator_results + title_results + text_phrase + everywhere
    # ensure books do exists & sort them
    for res in (author_results, translator_results, title_results, text_phrase, everywhere):
        res.sort(reverse=True)

    # We don't want to redirect to book text, but rather display result page even with one result.
    # if len(results) == 1:
    #     fragment_hits = filter(lambda h: 'fragment' in h, results[0].hits)
    #     if len(fragment_hits) == 1:
    #         #anchor = fragment_hits[0]['fragment']
    #         #frag = Fragment.objects.get(anchor=anchor)
    #         return HttpResponseRedirect(fragment_hits[0]['fragment'].get_absolute_url())
    #     return HttpResponseRedirect(results[0].book.get_absolute_url())
    if len(results) == 0:
        form = PublishingSuggestForm(initial={"books": query + ", "})
        return render_to_response('catalogue/search_no_hits.html',
                                  {'tags': tags,
                                   'prefix': query,
                                   "form": form,
                                   'did_you_mean': suggestion},
            context_instance=RequestContext(request))

    return render_to_response('catalogue/search_multiple_hits.html',
                              {'tags': tags,
                               'prefix': query,
                               'results': {'author': author_results,
                                           'translator': translator_results,
                                           'title': title_results,
                                           'content': text_phrase,
                                           'other': everywhere},
                               'did_you_mean': suggestion},
        context_instance=RequestContext(request))
