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

    tags = search.hint_tags(query, pdcounter=True, prefix=False)
    tags = split_tags(tags)

    results_parts = []

    search_fields = []
    fieldsets = (
        (['authors'], True),
        (['title'], True),
        (['metadata'], True),
        (['text', 'themes_pl'], False),
    )
    for fieldset, is_book in fieldsets:
        search_fields += fieldset
        results_parts.append(search.search_words(words, search_fields, book=is_book))

    results = []
    ids_results = {}
    for results_part in results_parts:
        for result in sorted(SearchResult.aggregate(results_part), reverse=True):
            book_id = result.book_id
            if book_id in ids_results:
                ids_results[book_id].merge(result)
            else:
                results.append(result)
                ids_results[book_id] = result

    for result in results:
        search.get_snippets(result, query, num=3)

    suggestion = u''

    def ensure_exists(r):
        try:
            return r.book
        except Book.DoesNotExist:
            return False

    results = filter(ensure_exists, results)

    if not results:
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
            'tags': tags['author'] + tags['kind'] + tags['genre'] + tags['epoch'] + tags['theme'],
            'prefix': query,
            'results': results,
            'did_you_mean': suggestion
        },
        context_instance=RequestContext(request))
