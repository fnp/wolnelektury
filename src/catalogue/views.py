# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from collections import OrderedDict
import re
import random

from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponsePermanentRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.http import urlquote_plus
from django.utils import translation
from django.utils.translation import ugettext as _, ugettext_lazy

from ajaxable.utils import AjaxableFormView
from pdcounter.models import BookStub, Author
from pdcounter import views as pdcounter_views
from picture.models import Picture, PictureArea
from ssify import ssi_included, ssi_expect, SsiVariable as Var
from suggest.forms import PublishingSuggestForm
from catalogue import constants
from catalogue import forms
from catalogue.helpers import get_top_level_related_tags
from catalogue.models import Book, Collection, Tag, Fragment
from catalogue.utils import split_tags

staff_required = user_passes_test(lambda user: user.is_staff)


def catalogue(request):
    return render(request, 'catalogue/catalogue.html', {
        'books': Book.objects.filter(parent=None).order_by('sort_key_author', 'sort_key'),
        'pictures': Picture.objects.order_by('sort_key_author', 'sort_key'),
        'collections': Collection.objects.all(),
    })


def book_list(request, filter=None, get_filter=None, template_name='catalogue/book_list.html',
              nav_template_name='catalogue/snippets/book_list_nav.html',
              list_template_name='catalogue/snippets/book_list.html', context=None):
    """ generates a listing of all books, optionally filtered with a test function """
    if get_filter:
        filter = get_filter()
    books_by_author, orphans, books_by_parent = Book.book_list(filter)
    books_nav = OrderedDict()
    for tag in books_by_author:
        if books_by_author[tag]:
            books_nav.setdefault(tag.sort_key[0], []).append(tag)
    # WTF: dlaczego nie include?
    return render_to_response(template_name, {
        'rendered_nav': render_to_string(nav_template_name, {'books_nav': books_nav}),
        'rendered_book_list': render_to_string(list_template_name, {
            'books_by_author': books_by_author,
            'orphans': orphans,
            'books_by_parent': books_by_parent,
        })
    }, context_instance=RequestContext(request))


def audiobook_list(request):
    books = Book.objects.filter(media__type__in=('mp3', 'ogg')).distinct().order_by(
        'sort_key_author', 'sort_key')
    books = list(books)
    if len(books) > 3:
        best = random.sample(books, 3)
    else:
        best = books

    daisy = Book.objects.filter(media__type='daisy').distinct().order_by('sort_key_author', 'sort_key')

    return render(request, 'catalogue/audiobook_list.html', {
        'books': books,
        'best': best,
        'daisy': daisy,
        })


def daisy_list(request):
    return book_list(request, Q(media__type='daisy'),
                     template_name='catalogue/daisy_list.html',
                     )


def collection(request, slug):
    coll = get_object_or_404(Collection, slug=slug)
    return render(request, 'catalogue/collection.html', {'collection': coll})


def differentiate_tags(request, tags, ambiguous_slugs):
    beginning = '/'.join(tag.url_chunk for tag in tags)
    unparsed = '/'.join(ambiguous_slugs[1:])
    options = []
    for tag in Tag.objects.filter(slug=ambiguous_slugs[0]):
        options.append({
            'url_args': '/'.join((beginning, tag.url_chunk, unparsed)).strip('/'),
            'tags': [tag]
        })
    return render_to_response(
        'catalogue/differentiate_tags.html', {'tags': tags, 'options': options, 'unparsed': ambiguous_slugs[1:]},
        context_instance=RequestContext(request))


# TODO: Rewrite this hellish piece of code which tries to do everything
def tagged_object_list(request, tags='', list_type='default'):
    raw_tags = tags
    # preliminary tests and conditions
    gallery = list_type == 'gallery'
    audiobooks = list_type == 'audiobooks'
    try:
        tags = Tag.get_tag_list(tags)
    except Tag.DoesNotExist:
        # Perhaps the user is asking about an author in Public Domain
        # counter (they are not represented in tags)
        chunks = tags.split('/')
        if len(chunks) == 2 and chunks[0] == 'autor':
            return pdcounter_views.author_detail(request, chunks[1])
        else:
            raise Http404
    except Tag.MultipleObjectsReturned, e:
        # Ask the user to disambiguate
        return differentiate_tags(request, e.tags, e.ambiguous_slugs)
    except Tag.UrlDeprecationWarning, e:
        return HttpResponsePermanentRedirect(
            reverse('tagged_object_list', args=['/'.join(tag.url_chunk for tag in e.tags)]))

    try:
        if len(tags) > settings.MAX_TAG_LIST:
            raise Http404
    except AttributeError:
        pass

    # beginning of digestion
    theme_is_set = any(tag.category == 'theme' for tag in tags)
    shelf_is_set = any(tag.category == 'set' for tag in tags)
    only_shelf = shelf_is_set and len(tags) == 1
    only_my_shelf = only_shelf and request.user == tags[0].user
    tags_pks = [tag.pk for tag in tags]

    if gallery and shelf_is_set:
        raise Http404

    daisy = None
    if theme_is_set:
        # Only fragments (or pirctureareas) here.
        shelf_tags = [tag for tag in tags if tag.category == 'set']
        fragment_tags = [tag for tag in tags if tag.category != 'set']
        if gallery:
            fragments = PictureArea.tagged.with_all(fragment_tags)
        else:
            fragments = Fragment.tagged.with_all(fragment_tags)

        if shelf_tags:
            # TODO: Pictures on shelves not supported yet.
            books = Book.tagged.with_all(shelf_tags).order_by()
            fragments = fragments.filter(Q(book__in=books) | Q(book__ancestor__in=books))

        categories = split_tags(
            Tag.objects.usage_for_queryset(fragments, counts=True).exclude(pk__in=tags_pks),
        )

        objects = fragments
    else:
        if gallery:
            # TODO: Pictures on shelves not supported yet.
            if tags:
                objects = Picture.tagged.with_all(tags)
            else:
                objects = Picture.objects.all()
            areas = PictureArea.objects.filter(picture__in=objects)
            categories = split_tags(
                Tag.objects.usage_for_queryset(
                    objects, counts=True).exclude(pk__in=tags_pks),
                Tag.objects.usage_for_queryset(
                    areas, counts=True).filter(
                    category__in=('theme', 'thing')).exclude(
                    pk__in=tags_pks),
            )
        else:
            if tags:
                all_books = Book.tagged.with_all(tags)
            else:
                all_books = Book.objects.filter(parent=None)
            if shelf_is_set:
                objects = all_books
                related_book_tags = Tag.objects.usage_for_queryset(
                    objects, counts=True).exclude(
                    category='set').exclude(pk__in=tags_pks)
            else:
                if tags:
                    objects = Book.tagged_top_level(tags)
                else:
                    objects = all_books
                # WTF: was outside if, overwriting value assigned if shelf_is_set
                related_book_tags = get_top_level_related_tags(tags)

            if audiobooks:
                if objects != all_books:
                    all_books = all_books.filter(media__type__in=('mp3', 'ogg')).distinct()
                    objects = objects.filter(media__type__in=('mp3', 'ogg')).distinct()
                else:
                    all_books = objects = objects.filter(media__type__in=('mp3', 'ogg')).distinct()
                daisy = objects.filter(media__type='daisy').distinct().order_by('sort_key_author', 'sort_key')

            fragments = Fragment.objects.filter(book__in=all_books)

            categories = split_tags(
                related_book_tags,
                Tag.objects.usage_for_queryset(
                    fragments, counts=True).filter(
                    category='theme').exclude(pk__in=tags_pks),
            )
        objects = objects.order_by('sort_key_author', 'sort_key')

    objects = list(objects)
    if len(objects) > 3:
        best = random.sample(objects, 3)
    else:
        best = objects

    if not gallery and not objects and len(tags) == 1:
        tag = tags[0]
        if tag.category in ('theme', 'thing') and (
                PictureArea.tagged.with_any([tag]).exists() or
                Picture.tagged.with_any([tag]).exists()):
            return redirect('tagged_object_list_gallery', raw_tags, permanent=False)

    return render_to_response(
        'catalogue/tagged_object_list.html',
        {
            'object_list': objects,
            'categories': categories,
            'only_shelf': only_shelf,
            'only_my_shelf': only_my_shelf,
            'formats_form': forms.DownloadFormatsForm(),
            'tags': tags,
            'tag_ids': tags_pks,
            'theme_is_set': theme_is_set,
            'best': best,
            'list_type': list_type,
            'daisy': daisy,
        },
        context_instance=RequestContext(request))


def book_fragments(request, slug, theme_slug):
    book = get_object_or_404(Book, slug=slug)
    theme = get_object_or_404(Tag, slug=theme_slug, category='theme')
    fragments = Fragment.tagged.with_all([theme]).filter(
        Q(book=book) | Q(book__ancestor=book))

    return render_to_response('catalogue/book_fragments.html', {
        'book': book,
        'theme': theme,
        'fragments': fragments,
    }, context_instance=RequestContext(request))


def book_detail(request, slug):
    try:
        book = Book.objects.get(slug=slug)
    except Book.DoesNotExist:
        return pdcounter_views.book_stub_detail(request, slug)

    return render_to_response('catalogue/book_detail.html', {
        'book': book,
        'tags': book.tags.exclude(category__in=('set', 'theme')),
        'book_children': book.children.all().order_by('parent_number', 'sort_key'),
    }, context_instance=RequestContext(request))


def get_audiobooks(book):
    ogg_files = {}
    for m in book.media.filter(type='ogg').order_by().iterator():
        ogg_files[m.name] = m

    audiobooks = []
    have_oggs = True
    projects = set()
    for mp3 in book.media.filter(type='mp3').iterator():
        # ogg files are always from the same project
        meta = mp3.extra_info
        project = meta.get('project')
        if not project:
            # temporary fallback
            project = u'CzytamySłuchając'

        projects.add((project, meta.get('funded_by', '')))

        media = {'mp3': mp3}

        ogg = ogg_files.get(mp3.name)
        if ogg:
            media['ogg'] = ogg
        else:
            have_oggs = False
        audiobooks.append(media)

    projects = sorted(projects)
    return audiobooks, projects, have_oggs


# używane tylko do audiobook_tree, które jest używane tylko w snippets/audiobook_list.html, które nie jest używane
def player(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if not book.has_media('mp3'):
        raise Http404

    audiobooks, projects, have_oggs = get_audiobooks(book)

    # extra_info = book.extra_info

    return render_to_response('catalogue/player.html', {
        'book': book,
        'audiobook': '',
        'audiobooks': audiobooks,
        'projects': projects,
    }, context_instance=RequestContext(request))


def book_text(request, slug):
    book = get_object_or_404(Book, slug=slug)

    if not book.has_html_file():
        raise Http404
    return render_to_response('catalogue/book_text.html', {'book': book,}, context_instance=RequestContext(request))


# ==========
# = Search =
# ==========

def _no_diacritics_regexp(query):
    """ returns a regexp for searching for a query without diacritics

    should be locale-aware """
    names = {
        u'a': u'aąĄ', u'c': u'cćĆ', u'e': u'eęĘ', u'l': u'lłŁ', u'n': u'nńŃ', u'o': u'oóÓ', u's': u'sśŚ',
        u'z': u'zźżŹŻ',
        u'ą': u'ąĄ', u'ć': u'ćĆ', u'ę': u'ęĘ', u'ł': u'łŁ', u'ń': u'ńŃ', u'ó': u'óÓ', u'ś': u'śŚ', u'ź': u'źŹ',
        u'ż': u'żŻ'
        }

    def repl(m):
        l = m.group()
        return u"(%s)" % '|'.join(names[l])

    return re.sub(u'[%s]' % (u''.join(names.keys())), repl, query)


def unicode_re_escape(query):
    """ Unicode-friendly version of re.escape """
    return re.sub(r'(?u)(\W)', r'\\\1', query)


def _word_starts_with(name, prefix):
    """returns a Q object getting models having `name` contain a word
    starting with `prefix`

    We define word characters as alphanumeric and underscore, like in JS.

    Works for MySQL, PostgreSQL, Oracle.
    For SQLite, _sqlite* version is substituted for this.
    """
    kwargs = {}

    prefix = _no_diacritics_regexp(unicode_re_escape(prefix))
    # can't use [[:<:]] (word start),
    # but we want both `xy` and `(xy` to catch `(xyz)`
    kwargs['%s__iregex' % name] = u"(^|[^[:alnum:]_])%s" % prefix

    return Q(**kwargs)


def _word_starts_with_regexp(prefix):
    prefix = _no_diacritics_regexp(unicode_re_escape(prefix))
    return ur"(^|(?<=[^\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ]))%s" % prefix


def _sqlite_word_starts_with(name, prefix):
    """ version of _word_starts_with for SQLite

    SQLite in Django uses Python re module
    """
    kwargs = {'%s__iregex' % name: _word_starts_with_regexp(prefix)}
    return Q(**kwargs)


if hasattr(settings, 'DATABASES'):
    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
        _word_starts_with = _sqlite_word_starts_with
elif settings.DATABASE_ENGINE == 'sqlite3':
    _word_starts_with = _sqlite_word_starts_with


class App:
    def __init__(self, name, view):
        self.name = name
        self._view = view
        self.lower = name.lower()
        self.category = 'application'

    def view(self):
        return reverse(*self._view)

_apps = (
    App(u'Leśmianator', (u'lesmianator', )),
    )


def _tags_starting_with(prefix, user=None):
    prefix = prefix.lower()
    # PD counter
    book_stubs = BookStub.objects.filter(_word_starts_with('title', prefix))
    authors = Author.objects.filter(_word_starts_with('name', prefix))

    books = Book.objects.filter(_word_starts_with('title', prefix))
    tags = Tag.objects.filter(_word_starts_with('name', prefix))
    if user and user.is_authenticated():
        tags = tags.filter(~Q(category='set') | Q(user=user))
    else:
        tags = tags.exclude(category='set')

    prefix_regexp = re.compile(_word_starts_with_regexp(prefix))
    return list(books) + list(tags) + [app for app in _apps if prefix_regexp.search(app.lower)] + list(book_stubs) + \
        list(authors)


def _get_result_link(match, tag_list):
    if isinstance(match, Tag):
        return reverse('catalogue.views.tagged_object_list',
                       kwargs={'tags': '/'.join(tag.url_chunk for tag in tag_list + [match])})
    elif isinstance(match, App):
        return match.view()
    else:
        return match.get_absolute_url()


def _get_result_type(match):
    if isinstance(match, Book) or isinstance(match, BookStub):
        match_type = 'book'
    else:
        match_type = match.category
    return match_type


def books_starting_with(prefix):
    prefix = prefix.lower()
    return Book.objects.filter(_word_starts_with('title', prefix))


def find_best_matches(query, user=None):
    """ Finds a Book, Tag, BookStub or Author best matching a query.

    Returns a with:
      - zero elements when nothing is found,
      - one element when a best result is found,
      - more then one element on multiple exact matches

    Raises a ValueError on too short a query.
    """

    query = query.lower()
    if len(query) < 2:
        raise ValueError("query must have at least two characters")

    result = tuple(_tags_starting_with(query, user))
    # remove pdcounter stuff
    book_titles = set(match.pretty_title().lower() for match in result
                      if isinstance(match, Book))
    authors = set(match.name.lower() for match in result
                  if isinstance(match, Tag) and match.category == 'author')
    result = tuple(res for res in result if not (
                 (isinstance(res, BookStub) and res.pretty_title().lower() in book_titles) or
                 (isinstance(res, Author) and res.name.lower() in authors)
             ))

    exact_matches = tuple(res for res in result if res.name.lower() == query)
    if exact_matches:
        return exact_matches
    else:
        return tuple(result)[:1]


def search(request):
    tags = request.GET.get('tags', '')
    prefix = request.GET.get('q', '')

    try:
        tag_list = Tag.get_tag_list(tags)
    except (Tag.DoesNotExist, Tag.MultipleObjectsReturned, Tag.UrlDeprecationWarning):
        tag_list = []

    try:
        result = find_best_matches(prefix, request.user)
    except ValueError:
        return render_to_response(
            'catalogue/search_too_short.html', {'tags': tag_list, 'prefix': prefix},
            context_instance=RequestContext(request))

    if len(result) == 1:
        return HttpResponseRedirect(_get_result_link(result[0], tag_list))
    elif len(result) > 1:
        return render_to_response(
            'catalogue/search_multiple_hits.html',
            {
                'tags': tag_list, 'prefix': prefix,
                'results': ((x, _get_result_link(x, tag_list), _get_result_type(x)) for x in result)
            },
            context_instance=RequestContext(request))
    else:
        form = PublishingSuggestForm(initial={"books": prefix + ", "})
        return render_to_response(
            'catalogue/search_no_hits.html',
            {'tags': tag_list, 'prefix': prefix, "pubsuggest_form": form},
            context_instance=RequestContext(request))


def tags_starting_with(request):
    prefix = request.GET.get('q', '')
    # Prefix must have at least 2 characters
    if len(prefix) < 2:
        return HttpResponse('')
    tags_list = []
    result = ""
    for tag in _tags_starting_with(prefix, request.user):
        if tag.name not in tags_list:
            result += "\n" + tag.name
            tags_list.append(tag.name)
    return HttpResponse(result)


def json_tags_starting_with(request, callback=None):
    # Callback for JSONP
    prefix = request.GET.get('q', '')
    callback = request.GET.get('callback', '')
    # Prefix must have at least 2 characters
    if len(prefix) < 2:
        return HttpResponse('')
    tags_list = []
    for tag in _tags_starting_with(prefix, request.user):
        if tag.name not in tags_list:
            tags_list.append(tag.name)
    if request.GET.get('mozhint', ''):
        result = [prefix, tags_list]
    else:
        result = {"matches": tags_list}
    response = JsonResponse(result, safe=False)
    if callback:
        response.content = callback + "(" + response.content + ");"
    return response


# =========
# = Admin =
# =========
@login_required
@staff_required
def import_book(request):
    """docstring for import_book"""
    book_import_form = forms.BookImportForm(request.POST, request.FILES)
    if book_import_form.is_valid():
        try:
            book_import_form.save()
        except:
            import sys
            import pprint
            import traceback
            info = sys.exc_info()
            exception = pprint.pformat(info[1])
            tb = '\n'.join(traceback.format_tb(info[2]))
            return HttpResponse(
                    _("An error occurred: %(exception)s\n\n%(tb)s") % {'exception': exception, 'tb': tb},
                    mimetype='text/plain')
        return HttpResponse(_("Book imported successfully"))
    else:
        return HttpResponse(_("Error importing file: %r") % book_import_form.errors)


# info views for API

def book_info(request, book_id, lang='pl'):
    book = get_object_or_404(Book, id=book_id)
    # set language by hand
    translation.activate(lang)
    return render_to_response('catalogue/book_info.html', {'book': book}, context_instance=RequestContext(request))


def tag_info(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    return HttpResponse(tag.description)


def download_zip(request, format, slug=None):
    if format in Book.ebook_formats:
        url = Book.zip_format(format)
    elif format in ('mp3', 'ogg') and slug is not None:
        book = get_object_or_404(Book, slug=slug)
        url = book.zip_audiobooks(format)
    else:
        raise Http404('No format specified for zip package')
    return HttpResponseRedirect(urlquote_plus(settings.MEDIA_URL + url, safe='/?='))


class CustomPDFFormView(AjaxableFormView):
    form_class = forms.CustomPDFForm
    title = ugettext_lazy('Download custom PDF')
    submit = ugettext_lazy('Download')
    honeypot = True

    def __call__(self, *args, **kwargs):
        if settings.NO_CUSTOM_PDF:
            raise Http404('Custom PDF is disabled')
        return super(CustomPDFFormView, self).__call__(*args, **kwargs)

    def form_args(self, request, obj):
        """Override to parse view args and give additional args to the form."""
        return (obj,), {}

    def get_object(self, request, slug, *args, **kwargs):
        return get_object_or_404(Book, slug=slug)

    def context_description(self, request, obj):
        return obj.pretty_title()


####
# Includes
####


@ssi_included
def book_mini(request, pk, with_link=True):
    book = get_object_or_404(Book, pk=pk)
    author_str = ", ".join(tag.name for tag in book.tags.filter(category='author'))
    return render(request, 'catalogue/book_mini_box.html', {
        'book': book,
        'author_str': author_str,
        'with_link': with_link,
        'show_lang': book.language_code() != settings.LANGUAGE_CODE,
    })


@ssi_included(get_ssi_vars=lambda pk: (lambda ipk: (
        ('ssify.get_csrf_token',),
        ('social_tags.likes_book', (ipk,)),
        ('social_tags.book_shelf_tags', (ipk,)),
    ))(ssi_expect(pk, int)))
def book_short(request, pk):
    book = get_object_or_404(Book, pk=pk)
    stage_note, stage_note_url = book.stage_note()
    audiobooks, projects, have_oggs = get_audiobooks(book)

    return render(request, 'catalogue/book_short.html', {
        'book': book,
        'has_audio': book.has_media('mp3'),
        'main_link': book.get_absolute_url(),
        'parents': book.parents(),
        'tags': split_tags(book.tags.exclude(category__in=('set', 'theme'))),
        'show_lang': book.language_code() != settings.LANGUAGE_CODE,
        'stage_note': stage_note,
        'stage_note_url': stage_note_url,
        'audiobooks': audiobooks,
        'have_oggs': have_oggs,
    })


@ssi_included(
    get_ssi_vars=lambda pk: book_short.get_ssi_vars(pk) +
    (lambda ipk: (
        ('social_tags.choose_cite', [ipk]),
        ('catalogue_tags.choose_fragment', [ipk], {
            'unless': Var('social_tags.choose_cite', [ipk])}),
    ))(ssi_expect(pk, int)))
def book_wide(request, pk):
    book = get_object_or_404(Book, pk=pk)
    stage_note, stage_note_url = book.stage_note()
    extra_info = book.extra_info
    audiobooks, projects, have_oggs = get_audiobooks(book)

    return render(request, 'catalogue/book_wide.html', {
        'book': book,
        'has_audio': book.has_media('mp3'),
        'parents': book.parents(),
        'tags': split_tags(book.tags.exclude(category__in=('set', 'theme'))),
        'show_lang': book.language_code() != settings.LANGUAGE_CODE,
        'stage_note': stage_note,
        'stage_note_url': stage_note_url,

        'main_link': reverse('book_text', args=[book.slug]) if book.html_file else None,
        'extra_info': extra_info,
        'hide_about': extra_info.get('about', '').startswith('http://wiki.wolnepodreczniki.pl'),
        'audiobooks': audiobooks,
        'have_oggs': have_oggs,
    })


@ssi_included
def fragment_short(request, pk):
    fragment = get_object_or_404(Fragment, pk=pk)
    return render(request, 'catalogue/fragment_short.html', {'fragment': fragment})


@ssi_included
def fragment_promo(request, pk):
    fragment = get_object_or_404(Fragment, pk=pk)
    return render(request, 'catalogue/fragment_promo.html', {'fragment': fragment})


@ssi_included
def tag_box(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    assert tag.category != 'set'

    return render(request, 'catalogue/tag_box.html', {
        'tag': tag,
    })


@ssi_included
def collection_box(request, pk):
    obj = get_object_or_404(Collection, pk=pk)

    return render(request, 'catalogue/collection_box.html', {
        'obj': obj,
    })


def tag_catalogue(request, category):
    if category == 'theme':
        tags = Tag.objects.usage_for_model(
            Fragment, counts=True).filter(category='theme')
    else:
        tags = list(get_top_level_related_tags((), categories=(category,)))

    described_tags = [tag for tag in tags if tag.description]

    if len(described_tags) > 4:
        best = random.sample(described_tags, 4)
    else:
        best = described_tags

    return render(request, 'catalogue/tag_catalogue.html', {
        'tags': tags,
        'best': best,
        'title': constants.CATEGORIES_NAME_PLURAL[category],
        'whole_category': constants.WHOLE_CATEGORY[category],
    })


def collections(request):
    objects = Collection.objects.all()

    if len(objects) > 3:
        best = random.sample(objects, 3)
    else:
        best = objects

    return render(request, 'catalogue/collections.html', {
        'objects': objects,
        'best': best,
    })
