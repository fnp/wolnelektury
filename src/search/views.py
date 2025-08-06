# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.conf import settings
from django.shortcuts import render
from django.views.decorators import cache
from django.http import HttpResponse, JsonResponse
from sorl.thumbnail import get_thumbnail

import catalogue.models
import infopages.models
import social.models
from .forms import SearchFilters
import re
import json

from wolnelektury.utils import re_escape


query_syntax_chars = re.compile(r"[\\/*:(){}?.[\]+]")


def remove_query_syntax_chars(query, replace=' '):
    return query_syntax_chars.sub(replace, query)


def get_hints(prefix, user=None, limit=10):
    if not prefix: return []
    data = []
    if len(data) < limit:
        authors = catalogue.models.Tag.objects.filter(
            category='author', name_pl__iregex='\m' + prefix).only('name', 'id', 'slug', 'category')
        data.extend([
            {
                'type': 'author',
                'label': author.name,
                'url': author.get_absolute_url(),
                'img': get_thumbnail(author.photo, '72x72', crop='top').url if author.photo else '',
                'slug': author.slug,
            }
            for author in authors[:limit - len(data)]
        ])
    
    if user is not None and user.is_authenticated and len(data) < limit:
        tags = social.models.UserList.objects.filter(
            user=user, name__iregex='\m' + prefix).only('name', 'id', 'slug')
        data.extend([
            {
                'type': 'userlist',
                'label': tag.name,
                'url': tag.get_absolute_url(),
                'slug': tag.slug,
            }
            for tag in tags[:limit - len(data)]
        ])
    if len(data) < limit:
        tags = catalogue.models.Tag.objects.filter(
            category__in=('theme', 'genre', 'epoch', 'kind'), name_pl__iregex='\m' + prefix).only('name', 'id', 'slug', 'category')
        data.extend([
            {
                'type': tag.category,
                'label': tag.name,
                'url': tag.get_absolute_url(),
                'slug': tag.slug,
            }
            for tag in tags[:limit - len(data)]
        ])
    if len(data) < limit:
        collections = catalogue.models.Collection.objects.filter(
            title_pl__iregex='\m' + prefix).only('title', 'slug')
        data.extend([
            {
                'type': 'collection',
                'label': collection.title,
                'url': collection.get_absolute_url(),
                'slug': collection.slug,
            }
            for collection in collections[:limit - len(data)]
        ])
    if len(data) < limit:
        for b in catalogue.models.Book.objects.filter(findable=True, title__iregex='\m' + prefix)[:limit-len(data)]:
            author_str = b.author_unicode()
            translator = b.translator()
            if translator:
                author_str += ' (tłum. ' + translator + ')'
            data.append(
                {
                    'type': 'book',
                    'label': b.title,
                    'author': author_str,
                    'url': b.get_absolute_url(),
                    'img': get_thumbnail(b.cover_clean, '72x72').url if b.cover_clean else '',
                    'slug': b.slug,
                }
            )
    if len(data) < limit:
        infos = infopages.models.InfoPage.objects.filter(
            published=True,
            findable=True,
            title_pl__iregex='\m' + prefix).only('title', 'id', 'slug')
        data.extend([
            {
                'type': 'info',
                'label': info.title,
                'url': info.get_absolute_url(),
                'slug': info.slug,
            }
            for info in infos[:limit - len(data)]
        ])
    return data


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

    data = get_hints(
        prefix,
        user=request.user if request.user.is_authenticated else None,
        limit=limit
    )

    if mozhint:
        data = [
            prefix,
            [
                item['label']
                for item in data
            ],
            [
                item.get('author', '')
                for item in data
            ],
            [
                item['url']
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
