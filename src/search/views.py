# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators import cache
from django.http import HttpResponse, JsonResponse

from catalogue.utils import split_tags
from catalogue.models import Book, Tag
from search.index import Search, SearchResult
from suggest.forms import PublishingSuggestForm
import re
import json

from wolnelektury.utils import re_escape


def match_word_re(word):
    if 'sqlite' in settings.DATABASES['default']['ENGINE']:
        return r"\b%s\b" % word
    elif 'mysql' in settings.DATABASES['default']['ENGINE']:
        return "[[:<:]]%s[[:>:]]" % word


query_syntax_chars = re.compile(r"[\\/*:(){}]")


def remove_query_syntax_chars(query, replace=' '):
    return query_syntax_chars.sub(replace, query)


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

    prefix = re_escape(' '.join(remove_query_syntax_chars(prefix).split()))

    try:
        limit = int(request.GET.get('max', ''))
    except ValueError:
        limit = 20
    else:
        if limit < 1:
            limit = 20

    authors = Tag.objects.filter(
        category='author', name_pl__iregex='\m' + prefix).only('name', 'id', 'slug', 'category')
    data = [
        {
            'label': author.name,
            'id': author.id,
            'url': author.get_absolute_url(),
        }
        for author in authors[:limit]
    ]
    if len(data) < limit:
        data += [
            {
                'label': b.title,
                'author': b.author_unicode(),
                'id': b.id,
                'url': b.get_absolute_url()
            }
            for b in Book.objects.filter(title__iregex='\m' + prefix)[:limit-len(data)]
        ]
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
