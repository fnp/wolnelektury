# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.shortcuts import render
from django.views.decorators import cache
from django.http import HttpResponse, JsonResponse

from catalogue.models import Book, Tag
from .forms import SearchFilters
import re
import json

from wolnelektury.utils import re_escape


query_syntax_chars = re.compile(r"[\\/*:(){}?.[\]+]")


def remove_query_syntax_chars(query, replace=' '):
    return query_syntax_chars.sub(replace, query)


@cache.never_cache
def hint(request, mozhint=False, param='term'):
    prefix = request.GET.get(param, '')
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
        for b in Book.objects.filter(findable=True, title__iregex='\m' + prefix)[:limit-len(data)]:
            author_str = b.author_unicode()
            translator = b.translator()
            if translator:
                author_str += ' (tłum. ' + translator + ')'
            data.append(
                {
                    'label': b.title,
                    'author': author_str,
                    'id': b.id,
                    'url': b.get_absolute_url()
                }
            )

    if mozhint:
        data = [
            prefix,
            [
                item['label']
                for item in data
            ]
        ]

    callback = request.GET.get('callback', None)
    if callback:
        return HttpResponse("%s(%s);" % (callback, json.dumps(data)),
                            content_type="application/json; charset=utf-8")
    else:
        return JsonResponse(data, safe=False)



@cache.never_cache
def search(request):
    filters = SearchFilters(request.GET)
    ctx = {
        'title': 'Wynik wyszukiwania',
        'query': request.GET.get('q', ''),
        'filters': filters,
    }
    if filters.is_valid():
        ctx['results'] = filters.results()
        for k, v in ctx['results'].items():
            if v:
                ctx['hasresults'] = True
                break
    return render(request, 'search/results.html', ctx)
