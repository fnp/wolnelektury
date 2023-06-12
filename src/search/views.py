# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators import cache
from django.http import HttpResponse, JsonResponse

from catalogue.models import Book, Tag
from pdcounter.models import Author
from picture.models import Picture
from search.index import Search, SearchResult, PictureResult
from .forms import SearchFilters
from suggest.forms import PublishingSuggestForm
import re
import json

from wolnelektury.utils import re_escape


def match_word_re(word):
    if 'sqlite' in settings.DATABASES['default']['ENGINE']:
        return r"\b%s\b" % word
    elif 'mysql' in settings.DATABASES['default']['ENGINE']:
        return "[[:<:]]%s[[:>:]]" % word


query_syntax_chars = re.compile(r"[\\/*:(){}?.[\]+]")


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


@cache.never_cache
def main(request):
    if request.EXPERIMENTS['layout'].value:
        return search(request)

    query = request.GET.get('q', '')

    format = request.GET.get('format')
    lang = request.GET.get('lang')
    epoch = request.GET.get('epoch')
    kind = request.GET.get('kind')
    genre = request.GET.get('genre')

    if len(query) < 2:
        return render(
            request, 'catalogue/search_too_short.html',
            {'prefix': query})
    elif len(query) > 256:
        return render(
            request, 'catalogue/search_too_long.html',
            {'prefix': query})

    query = prepare_query(query)
    if not (format or lang or epoch or kind or genre):
        pd_authors = search_pd_authors(query)
    else:
        pd_authors = []
    if not format or format != 'obraz':
        books = search_books(
            query,
            lang=lang,
            only_audio=format=='audio',
            only_synchro=format=='synchro',
            epoch=epoch,
            kind=kind,
            genre=genre
        )
    else:
        books = []
    if (not format or format == 'obraz') and not lang:
        pictures = search_pictures(
            query,
            epoch=epoch,
            kind=kind,
            genre=genre
        )
    else:
        pictures = []
    
    suggestion = ''

    if not (books or pictures or pd_authors):
        form = PublishingSuggestForm(initial={"books": query + ", "})
        return render(
            request,
            'catalogue/search_no_hits.html',
            {
                'form': form,
                'did_you_mean': suggestion
            })

    if not (books or pictures) and len(pd_authors) == 1:
        return HttpResponseRedirect(pd_authors[0].get_absolute_url())

    return render(
        request,
        'catalogue/search_multiple_hits.html',
        {
            'pd_authors': pd_authors,
            'books': books,
            'pictures': pictures,
            'did_you_mean': suggestion,
            'set': {
                'lang': lang,
                'format': format,
                'epoch': epoch,
                'kind': kind,
                'genre': genre,
            },
            'tags': {
                'epoch': Tag.objects.filter(category='epoch', for_books=True),
                'genre': Tag.objects.filter(category='genre', for_books=True),
                'kind': Tag.objects.filter(category='kind', for_books=True),
            },
        })

def search_books(query, lang=None, only_audio=False, only_synchro=False, epoch=None, kind=None, genre=None):
    search = Search()
    results_parts = []
    search_fields = []
    words = query.split()
    fieldsets = (
        (['authors', 'authors_nonstem'], True),
        (['title', 'title_nonstem'], True),
        (['metadata', 'metadata_nonstem'], True),
        (['text', 'text_nonstem', 'themes_pl', 'themes_pl_nonstem'], False),
    )
    for fields, is_book in fieldsets:
        search_fields += fields
        results_parts.append(search.search_words(words, search_fields, required=fields, book=is_book))
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
    descendant_ids = set(
        Book.objects.filter(id__in=ids_results, ancestor__in=ids_results).values_list('id', flat=True))
    results = [result for result in results if result.book_id not in descendant_ids]
    for result in results:
        search.get_snippets(result, query, num=3)

    def ensure_exists(r):
        try:
            if not r.book:
                return False
        except Book.DoesNotExist:
            return False

        if lang and r.book.language != lang:
            return False
        if only_audio and not r.book.has_mp3_file():
            return False
        if only_synchro and not r.book.has_daisy_file():
            return False
        if epoch and not r.book.tags.filter(category='epoch', slug=epoch).exists():
            return False
        if kind and not r.book.tags.filter(category='kind', slug=kind).exists():
            return False
        if genre and not r.book.tags.filter(category='genre', slug=genre).exists():
            return False

        return True

    results = [r for r in results if ensure_exists(r)]
    return results


def search_pictures(query, epoch=None, kind=None, genre=None):
    search = Search()
    results_parts = []
    search_fields = []
    words = query.split()
    fieldsets = (
        (['authors', 'authors_nonstem'], True),
        (['title', 'title_nonstem'], True),
        (['metadata', 'metadata_nonstem'], True),
        (['themes_pl', 'themes_pl_nonstem'], False),
    )
    for fields, is_book in fieldsets:
        search_fields += fields
        results_parts.append(search.search_words(words, search_fields, required=fields, book=is_book, picture=True))
    results = []
    ids_results = {}
    for results_part in results_parts:
        for result in sorted(PictureResult.aggregate(results_part), reverse=True):
            picture_id = result.picture_id
            if picture_id in ids_results:
                ids_results[picture_id].merge(result)
            else:
                results.append(result)
                ids_results[picture_id] = result

    def ensure_exists(r):
        try:
            if not r.picture:
                return False
        except Picture.DoesNotExist:
            return False

        if epoch and not r.picture.tags.filter(category='epoch', slug=epoch).exists():
            return False
        if kind and not r.picture.tags.filter(category='kind', slug=kind).exists():
            return False
        if genre and not r.picture.tags.filter(category='genre', slug=genre).exists():
            return False

        return True

    results = [r for r in results if ensure_exists(r)]
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
