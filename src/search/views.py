# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators import cache
from django.http import HttpResponse, JsonResponse

from catalogue.models import Book, Tag
from pdcounter.models import Author
from picture.models import Picture
from search.index import Search, SearchResult, PictureResult
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
    if len(query) < 2:
        return render_to_response(
            'catalogue/search_too_short.html', {'prefix': query},
            context_instance=RequestContext(request))
    elif len(query) > 256:
        return render_to_response(
            'catalogue/search_too_long.html', {'prefix': query}, context_instance=RequestContext(request))

    query = prepare_query(query)
    pd_authors = search_pd_authors(query)
    books = search_books(query)
    pictures = search_pictures(query)
    suggestion = u''

    if not (books or pictures or pd_authors):
        form = PublishingSuggestForm(initial={"books": query + ", "})
        return render_to_response(
            'catalogue/search_no_hits.html',
            {
                'form': form,
                'did_you_mean': suggestion
            },
            context_instance=RequestContext(request))

    if not (books or pictures) and len(pd_authors) == 1:
        return HttpResponseRedirect(pd_authors[0].get_absolute_url())

    return render_to_response(
        'catalogue/search_multiple_hits.html',
        {
            'pd_authors': pd_authors,
            'books': books,
            'pictures': pictures,
            'did_you_mean': suggestion
        },
        context_instance=RequestContext(request))


def search_books(query):
    search = Search()
    # results_parts = []
    # search_fields = []
    words = query.split()
    fieldsets = (
        (['authors'], True, 8),
        (['title'], True, 4),
        (['metadata'], True, 2),
        (['text', 'themes_pl'], False, 1),
    )
    # for fields, is_book in fieldsets:
    #     search_fields += fields
    #     results_parts.append(search.search_words(words, search_fields, required=fields, book=is_book))
    query_results = search.search_words(words, fieldsets)
    results = []
    ids_results = {}
    # for results_part in results_parts:
    for result in sorted(SearchResult.aggregate(query_results), reverse=True):
        book_id = result.book_id
        if book_id in ids_results:
            ids_results[book_id].merge(result)
        else:
            results.append(result)
            ids_results[book_id] = result
    descendant_ids = set(
        Book.objects.filter(id__in=ids_results, ancestor__in=ids_results).values_list('id', flat=True))
    results = [result for result in results if result.book_id not in descendant_ids]
    for result in results:
        search.get_snippets(result, query, num=3)

    def ensure_exists(r):
        try:
            return r.book
        except Book.DoesNotExist:
            return False

    results = filter(ensure_exists, results)
    return results


def search_pictures(query):
    search = Search()
    # results_parts = []
    # search_fields = []
    words = query.split()
    fieldsets = (
        (['authors'], True, 8),
        (['title'], True, 4),
        (['metadata'], True, 2),
        (['themes_pl'], False, 1),
    )
    # for fields, is_book in fieldsets:
    #     search_fields += fields
    #     results_parts.append(search.search_words(words, search_fields, required=fields, book=is_book, picture=True))
    query_results = search.search_words(words, fieldsets, picture=True)
    results = []
    ids_results = {}
    # for results_part in results_parts:
    for result in sorted(PictureResult.aggregate(query_results), reverse=True):
        picture_id = result.picture_id
        if picture_id in ids_results:
            ids_results[picture_id].merge(result)
        else:
            results.append(result)
            ids_results[picture_id] = result

    def ensure_exists(r):
        try:
            return r.picture
        except Picture.DoesNotExist:
            return False

    results = filter(ensure_exists, results)
    return results


def search_pd_authors(query):
    pd_authors = Author.objects.filter(name__icontains=query)
    existing_slugs = Tag.objects.filter(
        category='author', slug__in=list(pd_authors.values_list('slug', flat=True))) \
        .values_list('slug', flat=True)
    pd_authors = pd_authors.exclude(slug__in=existing_slugs)
    return pd_authors


def prepare_query(query):
    query = ' '.join(query.split())
    # filter out private use characters
    import unicodedata
    query = ''.join(ch for ch in query if unicodedata.category(ch) != 'Co')
    query = remove_query_syntax_chars(query)

    words = query.split()
    if len(words) > 10:
        query = ' '.join(words[:10])
    return query
