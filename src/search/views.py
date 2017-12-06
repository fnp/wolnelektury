# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators import cache
from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext as _

from catalogue.utils import split_tags
from catalogue.models import Book
from pdcounter.models import Author as PDCounterAuthor, BookStub as PDCounterBook
from search.index import Search, SearchResult
from suggest.forms import PublishingSuggestForm
import re
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


@cache.never_cache
def hint(request):
    prefix = request.GET.get('term', '')
    if len(prefix) < 2:
        return JsonResponse([], safe=False)

    prefix = remove_query_syntax_chars(prefix)

    search = Search()
    # tagi beda ograniczac tutaj
    # ale tagi moga byc na ksiazce i na fragmentach
    # jezeli tagi dot tylko ksiazki, to wazne zeby te nowe byly w tej samej ksiazce
    # jesli zas dotycza themes, to wazne, zeby byly w tym samym fragmencie.

    def is_dupe(tag):
        if isinstance(tag, PDCounterAuthor):
            if filter(lambda t: t.slug == tag.slug and t != tag, tags):
                return True
        elif isinstance(tag, PDCounterBook):
            if filter(lambda b: b.slug == tag.slug, tags):
                return True
        return False

    def category_name(c):
        if c.startswith('pd_'):
            c = c[len('pd_'):]
        return _(c)

    try:
        limit = int(request.GET.get('max', ''))
    except ValueError:
        limit = -1
    else:
        if limit < 1:
            limit = -1

    data = []

    tags = search.hint_tags(prefix, pdcounter=True)
    tags = filter(lambda t: not is_dupe(t), tags)
    for t in tags:
        if not limit:
            break
        limit -= 1
        data.append({
            'label': t.name,
            'category': category_name(t.category),
            'id': t.id,
            'url': t.get_absolute_url()
            })
    if limit:
        books = search.hint_books(prefix)
        for b in books:
            if not limit:
                break
            limit -= 1
            data.append({
                'label': '<cite>%s</cite>, %s' % (b.title, b.author_unicode()),
                'category': _('book'),
                'id': b.id,
                'url': b.get_absolute_url()
                })

    callback = request.GET.get('callback', None)
    if callback:
        return HttpResponse("%s(%s);" % (callback, json.dumps(data)),
                            content_type="application/json; charset=utf-8")
    else:
        return JsonResponse(data, safe=False)


@cache.never_cache
def main(request):
    query = request.GET.get('q', '')
    query = ' '.join(query.split())
    # filter out private use characters
    import unicodedata
    query = ''.join(ch for ch in query if unicodedata.category(ch) != 'Co')

    if len(query) < 2:
        return render_to_response(
            'catalogue/search_too_short.html', {'prefix': query},
            context_instance=RequestContext(request))
    elif len(query) > 256:
        return render_to_response(
            'catalogue/search_too_long.html', {'prefix': query}, context_instance=RequestContext(request))

    query = remove_query_syntax_chars(query)

    words = query.split()
    if len(words) > 10:
        query = ' '.join(words[:10])

    search = Search()

    # change hints
    tags = search.hint_tags(query, pdcounter=True, prefix=False)
    tags = split_tags(tags)

    author_results = search.search_words(words, ['authors'])

    title_results = search.search_words(words, ['title'])

    author_title_mixed = search.search_words(words, ['authors', 'title', 'metadata'])
    author_title_rest = []

    for b in author_title_mixed:
        also_in_mixed = filter(lambda ba: ba.book_id == b.book_id, author_results + title_results)
        for b2 in also_in_mixed:
            b2.boost *= 1.1
        if not also_in_mixed:
            author_title_rest.append(b)

    text_phrase = SearchResult.aggregate(search.search_words(words, ['text'], book=False))

    everywhere = search.search_words(words, ['metadata', 'text', 'themes_pl'], book=False)

    def already_found(results):
        def f(e):
            for r in results:
                if e.book_id == r.book_id:
                    e.boost = 0.9
                    results.append(e)
                    return True
            return False
        return f
    f = already_found(author_results + title_results + text_phrase)
    everywhere = filter(lambda x: not f(x), everywhere)

    author_results = SearchResult.aggregate(author_results, author_title_rest)
    title_results = SearchResult.aggregate(title_results)

    everywhere = SearchResult.aggregate(everywhere, author_title_rest)

    for field, res in [('authors', author_results),
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
    title_results = filter(ensure_exists, title_results)
    text_phrase = filter(ensure_exists, text_phrase)
    everywhere = filter(ensure_exists, everywhere)

    # ensure books do exists & sort them
    for res in (author_results, title_results, text_phrase):
        res.sort(reverse=True)

    if not (author_results or title_results or text_phrase or everywhere):
        form = PublishingSuggestForm(initial={"books": query + ", "})
        return render_to_response(
            'catalogue/search_no_hits.html',
            {
                'tags': tags,
                'prefix': query,
                'form': form,
                'did_you_mean': suggestion
            },
            context_instance=RequestContext(request))

    return render_to_response(
        'catalogue/search_multiple_hits.html',
        {
            'tags': tags,
            'prefix': query,
            'results': {
                'author': author_results,
                'title': title_results,
                'content': text_phrase,
                'other': everywhere
            },
            'did_you_mean': suggestion
        },
        context_instance=RequestContext(request))
