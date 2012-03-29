# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators import cache
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponsePermanentRedirect
from django.utils.translation import ugettext as _

from catalogue.utils import split_tags
from catalogue.models import Book, Tag, Fragment
from catalogue.views import JSONResponse
from search import Search, JVM, SearchResult
from lucene import StringReader
from suggest.forms import PublishingSuggestForm
import re
import enchant

dictionary = enchant.Dict('pl_PL')


def match_word_re(word):
    if 'sqlite' in settings.DATABASES['default']['ENGINE']:
        return r"\b%s\b" % word
    elif 'mysql' in settings.DATABASES['default']['ENGINE']:
        return "[[:<:]]%s[[:>:]]" % word


def did_you_mean(query, tokens):
    change = {}
    for t in tokens:
        authors = Tag.objects.filter(category='author', name__iregex=match_word_re(t))
        if len(authors) > 0:
            continue

        if not dictionary.check(t):
            try:
                change_to = dictionary.suggest(t)[0].lower()
                if change_to != t.lower():
                    change[t] = change_to
            except IndexError:
                pass

    if change == {}:
        return None

    for frm, to in change.items():
        query = query.replace(frm, to)

    return query

JVM.attachCurrentThread()
search = Search()


def hint(request):
    prefix = request.GET.get('term', '')
    if len(prefix) < 2:
        return JSONResponse([])
    JVM.attachCurrentThread()

    hint = search.hint()
    try:
        tags = request.GET.get('tags', '')
        hint.tags(Tag.get_tag_list(tags))
    except:
        pass

    # tagi beda ograniczac tutaj
    # ale tagi moga byc na ksiazce i na fragmentach
    # jezeli tagi dot tylko ksiazki, to wazne zeby te nowe byly w tej samej ksiazce
    # jesli zas dotycza themes, to wazne, zeby byly w tym samym fragmencie.

    tags = search.hint_tags(prefix, pdcounter=True)
    books = search.hint_books(prefix)

    def category_name(c):
        if c.startswith('pd_'):
            c = c[len('pd_'):]
        return _(c)

    return JSONResponse(
        [{'label': t.name,
          'category': category_name(t.category),
          'id': t.id,
          'url': t.get_absolute_url()}
          for t in tags] + \
          [{'label': b.title,
            'category': _('book'),
            'id': b.id,
            'url': b.get_absolute_url()}
            for b in books])


def main(request):
    results = {}
    JVM.attachCurrentThread()  # where to put this?

    results = None
    query = None
    fuzzy = False #0.8

    query = request.GET.get('q','')
    # book_id = request.GET.get('book', None)
    # book = None
    # if book_id is not None:
    #     book = get_object_or_404(Book, id=book_id)

    # hint = search.hint()
    # try:
    #     tag_list = Tag.get_tag_list(tags)
    # except:
    #     tag_list = []

    if len(query) < 2:
        return render_to_response('catalogue/search_too_short.html', {'prefix': query},
                                  context_instance=RequestContext(request))

    # hint.tags(tag_list)
    # if book:
    #     hint.books(book)
    tags = search.hint_tags(query, pdcounter=True, prefix=False, fuzzy=fuzzy)
    tags = split_tags(tags)

    toks = StringReader(query)
    tokens_cache = {}

    author_results = search.search_phrase(toks, 'authors', fuzzy=fuzzy, tokens_cache=tokens_cache)
    title_results = search.search_phrase(toks, 'title', fuzzy=fuzzy, tokens_cache=tokens_cache)

    # Boost main author/title results with mixed search, and save some of its results for end of list.
    # boost author, title results
    author_title_mixed = search.search_some(toks, ['authors', 'title', 'tags'], fuzzy=fuzzy, tokens_cache=tokens_cache)
    author_title_rest = []
    for b in author_title_mixed:
        bks = filter(lambda ba: ba.book_id == b.book_id, author_results + title_results)
        for b2 in bks:
            b2.boost *= 1.1
        if bks is []:
            author_title_rest.append(b)

    # Do a phrase search but a term search as well - this can give us better snippets then search_everywhere,
    # Because the query is using only one field.
    text_phrase = SearchResult.aggregate(
        search.search_phrase(toks, 'content', fuzzy=fuzzy, tokens_cache=tokens_cache, snippets=True, book=False, slop=4),
        search.search_some(toks, ['content'], tokens_cache=tokens_cache, snippets=True, book=False))

    everywhere = search.search_everywhere(toks, fuzzy=fuzzy, tokens_cache=tokens_cache)

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

    author_results = SearchResult.aggregate(author_results)
    title_results = SearchResult.aggregate(title_results)

    everywhere = SearchResult.aggregate(everywhere, author_title_rest)

    for res in [author_results, title_results, text_phrase, everywhere]:
        res.sort(reverse=True)
        for r in res:
            for h in r.hits:
                h['snippets'] = map(lambda s:
                                    re.subn(r"(^[ \t\n]+|[ \t\n]+$)", u"",
                                            re.subn(r"[ \t\n]*\n[ \t\n]*", u"\n", s)[0])[0], h['snippets'])

    suggestion = did_you_mean(query, search.get_tokens(toks, field="SIMPLE"))

    def ensure_exists(r):
        try:
            return r.book
        except Book.DoesNotExist:
            return False

    author_results = filter(ensure_exists, author_results)
    title_results = filter(ensure_exists, title_results)
    text_phrase = filter(ensure_exists, text_phrase)
    everywhere = filter(ensure_exists, everywhere)

    results = author_results + title_results + text_phrase + everywhere
    # ensure books do exists & sort them
    results.sort(reverse=True)

    if len(results) == 1:
        fragment_hits = filter(lambda h: 'fragment' in h, results[0].hits)
        if len(fragment_hits) == 1:
            #anchor = fragment_hits[0]['fragment']
            #frag = Fragment.objects.get(anchor=anchor)
            return HttpResponseRedirect(fragment_hits[0]['fragment'].get_absolute_url())
        return HttpResponseRedirect(results[0].book.get_absolute_url())
    elif len(results) == 0:
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
                               'results': { 'author': author_results,
                                            'title': title_results,
                                            'content': text_phrase,
                                            'other': everywhere},
                               'did_you_mean': suggestion},
        context_instance=RequestContext(request))
