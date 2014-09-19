# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from collections import OrderedDict
import re

from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponsePermanentRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.http import urlquote_plus
from django.utils import translation
from django.utils.translation import ugettext as _, ugettext_lazy

from ajaxable.utils import AjaxableFormView
from pdcounter import models as pdcounter_models
from pdcounter import views as pdcounter_views
from picture.models import Picture, PictureArea
from picture.views import picture_list_thumb
from ssify import ssi_included, ssi_expect, SsiVariable as V
from suggest.forms import PublishingSuggestForm
from catalogue import forms
from catalogue.helpers import get_top_level_related_tags
from catalogue import models
from catalogue.utils import split_tags, MultiQuerySet, SortedMultiQuerySet
from catalogue.templatetags.catalogue_tags import tag_list, collection_list

staff_required = user_passes_test(lambda user: user.is_staff)


def catalogue(request, as_json=False):
    common_categories = ('author',)
    split_categories = ('epoch', 'genre', 'kind')

    categories = split_tags(
        get_top_level_related_tags(categories=common_categories),
        models.Tag.objects.usage_for_model(
            models.Fragment, counts=True).filter(category='theme'),
        models.Tag.objects.usage_for_model(
            Picture, counts=True).filter(category__in=common_categories),
        models.Tag.objects.usage_for_model(
            PictureArea, counts=True).filter(
            category='theme')
    )
    book_categories = split_tags(
        get_top_level_related_tags(categories=split_categories)
        )
    picture_categories = split_tags(
        models.Tag.objects.usage_for_model(
            Picture, counts=True).filter(
            category__in=split_categories),
        )

    collections = models.Collection.objects.all()

    def render_tag_list(tags):
        render_to_string('catalogue/tag_list.html', tag_list(tags))

    def render_split(with_books, with_pictures):
        ctx = {}
        if with_books:
            ctx['books'] = render_tag_list(with_books)
        if with_pictures:
            ctx['pictures'] = render_tag_list(with_pictures)
        return render_to_string('catalogue/tag_list_split.html', ctx)

    output = {}
    output['theme'] = render_tag_list(categories.get('theme', []))
    for category in common_categories:
        output[category] = render_tag_list(categories.get(category, []))
    for category in split_categories:
        output[category] = render_split(
            book_categories.get(category, []),
            picture_categories.get(category, []))

    output['collections'] = render_to_string(
        'catalogue/collection_list.html', collection_list(collections))
    if as_json:
        return JsonResponse(output)
    else:
        return render_to_response('catalogue/catalogue.html', locals(),
            context_instance=RequestContext(request))


@ssi_included
def catalogue_json(request):
    return catalogue(request, True)


def book_list(request, filter=None, get_filter=None,
        template_name='catalogue/book_list.html',
        nav_template_name='catalogue/snippets/book_list_nav.html',
        list_template_name='catalogue/snippets/book_list.html',
        context=None,
        ):
    """ generates a listing of all books, optionally filtered with a test function """
    if get_filter:
        filter = get_filter()
    books_by_author, orphans, books_by_parent = models.Book.book_list(filter)
    books_nav = OrderedDict()
    for tag in books_by_author:
        if books_by_author[tag]:
            books_nav.setdefault(tag.sort_key[0], []).append(tag)
    rendered_nav = render_to_string(nav_template_name, locals())
    rendered_book_list = render_to_string(list_template_name, locals())
    return render_to_response(template_name, locals(),
        context_instance=RequestContext(request))


def audiobook_list(request):
    return book_list(request, Q(media__type='mp3') | Q(media__type='ogg'),
                     template_name='catalogue/audiobook_list.html',
                     list_template_name='catalogue/snippets/audiobook_list.html',
                     )


def daisy_list(request):
    return book_list(request, Q(media__type='daisy'),
                     template_name='catalogue/daisy_list.html',
                     )


def collection(request, slug):
    coll = get_object_or_404(models.Collection, slug=slug)
    if coll.kind == 'book':
        view = book_list
        tmpl = "catalogue/collection.html"
    elif coll.kind == 'picture':
        view = picture_list_thumb
        tmpl = "picture/collection.html"
    else:
        raise ValueError('How do I show this kind of collection? %s' % coll.kind)
    return view(request, get_filter=coll.get_query,
                     template_name=tmpl,
                     context={'collection': coll})


def differentiate_tags(request, tags, ambiguous_slugs):
    beginning = '/'.join(tag.url_chunk for tag in tags)
    unparsed = '/'.join(ambiguous_slugs[1:])
    options = []
    for tag in models.Tag.objects.filter(slug=ambiguous_slugs[0]):
        options.append({
            'url_args': '/'.join((beginning, tag.url_chunk, unparsed)).strip('/'),
            'tags': [tag]
        })
    return render_to_response('catalogue/differentiate_tags.html',
                {'tags': tags, 'options': options, 'unparsed': ambiguous_slugs[1:]},
                context_instance=RequestContext(request))


# TODO: Rewrite this hellish piece of code which tries to do everything
def tagged_object_list(request, tags=''):
    # preliminary tests and conditions
    try:
        tags = models.Tag.get_tag_list(tags)
    except models.Tag.DoesNotExist:
        # Perhaps the user is asking about an author in Public Domain
        # counter (they are not represented in tags)
        chunks = tags.split('/')
        if len(chunks) == 2 and chunks[0] == 'autor':
            return pdcounter_views.author_detail(request, chunks[1])
        else:
            raise Http404
    except models.Tag.MultipleObjectsReturned, e:
        # Ask the user to disambiguate
        return differentiate_tags(request, e.tags, e.ambiguous_slugs)
    except models.Tag.UrlDeprecationWarning, e:
        return HttpResponsePermanentRedirect(reverse('tagged_object_list', args=['/'.join(tag.url_chunk for tag in e.tags)]))

    try:
        if len(tags) > settings.MAX_TAG_LIST:
            raise Http404
    except AttributeError:
        pass

    # beginning of digestion
    theme_is_set = [tag for tag in tags if tag.category == 'theme']
    shelf_is_set = [tag for tag in tags if tag.category == 'set']
    only_shelf = shelf_is_set and len(tags) == 1
    only_my_shelf = only_shelf and request.user.is_authenticated() and request.user == tags[0].user
    tags_pks = [tag.pk for tag in tags]

    objects = None

    if theme_is_set:
        shelf_tags = [tag for tag in tags if tag.category == 'set']
        fragment_tags = [tag for tag in tags if tag.category != 'set']
        fragments = models.Fragment.tagged.with_all(fragment_tags)
        areas = PictureArea.tagged.with_all(fragment_tags)

        if shelf_tags:
            books = models.Book.tagged.with_all(shelf_tags).order_by()
            fragments = fragments.filter(Q(book__in=books) | Q(book__ancestor__in=books))
            areas = PictureArea.objects.none()

        categories = split_tags(
            models.Tag.objects.usage_for_queryset(fragments, counts=True
                ).exclude(pk__in=tags_pks),
            models.Tag.objects.usage_for_queryset(areas, counts=True
                ).exclude(pk__in=tags_pks)
            )

        # we want the Pictures to go first
        objects = MultiQuerySet(areas, fragments)
    else:
        all_books = models.Book.tagged.with_all(tags)
        if shelf_is_set:
            books = all_books.order_by('sort_key_author', 'title')
            pictures = Pictures.objects.none()
            related_book_tags = models.Tag.objects.usage_for_queryset(
                books, counts=True).exclude(
                category='set').exclude(pk__in=tags_pks)
        else:
            books = models.Book.tagged_top_level(tags).order_by(
                'sort_key_author', 'title')
            pictures = Picture.tagged.with_all(tags).order_by(
                'sort_key_author', 'title')
            related_book_tags = get_top_level_related_tags(tags)

        fragments = models.Fragment.objects.filter(book__in=all_books)
        areas = PictureArea.objects.filter(picture__in=pictures)

        categories = split_tags(
            related_book_tags,
            models.Tag.objects.usage_for_queryset(
                pictures, counts=True).exclude(pk__in=tags_pks),
            models.Tag.objects.usage_for_queryset(
                fragments, counts=True).filter(
                category='theme').exclude(pk__in=tags_pks),
            models.Tag.objects.usage_for_queryset(
                areas, counts=True).filter(
                category__in=('theme', 'thing')).exclude(
                pk__in=tags_pks),
        )

        objects = SortedMultiQuerySet(pictures, books,
            order_by=('sort_key_author', 'title'))

    return render_to_response('catalogue/tagged_object_list.html',
        {
            'object_list': objects,
            'categories': categories,
            'only_shelf': only_shelf,
            'only_my_shelf': only_my_shelf,
            'formats_form': forms.DownloadFormatsForm(),
            'tags': tags,
            'tags_ids': tags_pks,
            'theme_is_set': theme_is_set,
        },
        context_instance=RequestContext(request))


def book_fragments(request, slug, theme_slug):
    book = get_object_or_404(models.Book, slug=slug)
    theme = get_object_or_404(models.Tag, slug=theme_slug, category='theme')
    fragments = models.Fragment.tagged.with_all([theme]).filter(
        Q(book=book) | Q(book__ancestor=book))

    return render_to_response('catalogue/book_fragments.html', locals(),
        context_instance=RequestContext(request))


def book_detail(request, slug):
    try:
        book = models.Book.objects.get(slug=slug)
    except models.Book.DoesNotExist:
        return pdcounter_views.book_stub_detail(request, slug)

    book_children = book.children.all().order_by('parent_number', 'sort_key')
    return render_to_response('catalogue/book_detail.html', locals(),
        context_instance=RequestContext(request))


def player(request, slug):
    book = get_object_or_404(models.Book, slug=slug)
    if not book.has_media('mp3'):
        raise Http404

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

    extra_info = book.extra_info

    return render_to_response('catalogue/player.html', locals(),
        context_instance=RequestContext(request))


def book_text(request, slug):
    book = get_object_or_404(models.Book, slug=slug)

    if not book.has_html_file():
        raise Http404
    return render_to_response('catalogue/book_text.html', locals(),
        context_instance=RequestContext(request))


# ==========
# = Search =
# ==========

def _no_diacritics_regexp(query):
    """ returns a regexp for searching for a query without diacritics

    should be locale-aware """
    names = {
        u'a':u'aąĄ', u'c':u'cćĆ', u'e':u'eęĘ', u'l': u'lłŁ', u'n':u'nńŃ', u'o':u'oóÓ', u's':u'sśŚ', u'z':u'zźżŹŻ',
        u'ą':u'ąĄ', u'ć':u'ćĆ', u'ę':u'ęĘ', u'ł': u'łŁ', u'ń':u'ńŃ', u'ó':u'óÓ', u'ś':u'śŚ', u'ź':u'źŹ', u'ż':u'żŻ'
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
    kwargs = {}
    kwargs['%s__iregex' % name] = _word_starts_with_regexp(prefix)
    return Q(**kwargs)


if hasattr(settings, 'DATABASES'):
    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
        _word_starts_with = _sqlite_word_starts_with
elif settings.DATABASE_ENGINE == 'sqlite3':
    _word_starts_with = _sqlite_word_starts_with


class App():
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
    book_stubs = pdcounter_models.BookStub.objects.filter(_word_starts_with('title', prefix))
    authors = pdcounter_models.Author.objects.filter(_word_starts_with('name', prefix))

    books = models.Book.objects.filter(_word_starts_with('title', prefix))
    tags = models.Tag.objects.filter(_word_starts_with('name', prefix))
    if user and user.is_authenticated():
        tags = tags.filter(~Q(category='set') | Q(user=user))
    else:
        tags = tags.exclude(category='set')

    prefix_regexp = re.compile(_word_starts_with_regexp(prefix))
    return list(books) + list(tags) + [app for app in _apps if prefix_regexp.search(app.lower)] + list(book_stubs) + list(authors)


def _get_result_link(match, tag_list):
    if isinstance(match, models.Tag):
        return reverse('catalogue.views.tagged_object_list',
            kwargs={'tags': '/'.join(tag.url_chunk for tag in tag_list + [match])}
        )
    elif isinstance(match, App):
        return match.view()
    else:
        return match.get_absolute_url()


def _get_result_type(match):
    if isinstance(match, models.Book) or isinstance(match, pdcounter_models.BookStub):
        match_type = 'book'
    else:
        match_type = match.category
    return match_type


def books_starting_with(prefix):
    prefix = prefix.lower()
    return models.Book.objects.filter(_word_starts_with('title', prefix))


def find_best_matches(query, user=None):
    """ Finds a models.Book, Tag, models.BookStub or Author best matching a query.

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
                      if isinstance(match, models.Book))
    authors = set(match.name.lower() for match in result
                  if isinstance(match, models.Tag) and match.category == 'author')
    result = tuple(res for res in result if not (
                 (isinstance(res, pdcounter_models.BookStub) and res.pretty_title().lower() in book_titles)
                 or (isinstance(res, pdcounter_models.Author) and res.name.lower() in authors)
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
        tag_list = models.Tag.get_tag_list(tags)
    except:
        tag_list = []

    try:
        result = find_best_matches(prefix, request.user)
    except ValueError:
        return render_to_response('catalogue/search_too_short.html', {'tags':tag_list, 'prefix':prefix},
            context_instance=RequestContext(request))

    if len(result) == 1:
        return HttpResponseRedirect(_get_result_link(result[0], tag_list))
    elif len(result) > 1:
        return render_to_response('catalogue/search_multiple_hits.html',
            {'tags':tag_list, 'prefix':prefix, 'results':((x, _get_result_link(x, tag_list), _get_result_type(x)) for x in result)},
            context_instance=RequestContext(request))
    else:
        form = PublishingSuggestForm(initial={"books": prefix + ", "})
        return render_to_response('catalogue/search_no_hits.html',
            {'tags':tag_list, 'prefix':prefix, "pubsuggest_form": form},
            context_instance=RequestContext(request))


def tags_starting_with(request):
    prefix = request.GET.get('q', '')
    # Prefix must have at least 2 characters
    if len(prefix) < 2:
        return HttpResponse('')
    tags_list = []
    result = ""
    for tag in _tags_starting_with(prefix, request.user):
        if not tag.name in tags_list:
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
        if not tag.name in tags_list:
            tags_list.append(tag.name)
    if request.GET.get('mozhint', ''):
        result = [prefix, tags_list]
    else:
        result = {"matches": tags_list}
    return JsonResponse(result, callback)


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
            return HttpResponse(_("An error occurred: %(exception)s\n\n%(tb)s") % {'exception':exception, 'tb':tb}, mimetype='text/plain')
        return HttpResponse(_("Book imported successfully"))
    else:
        return HttpResponse(_("Error importing file: %r") % book_import_form.errors)


# info views for API

def book_info(request, id, lang='pl'):
    book = get_object_or_404(models.Book, id=id)
    # set language by hand
    translation.activate(lang)
    return render_to_response('catalogue/book_info.html', locals(),
        context_instance=RequestContext(request))


def tag_info(request, id):
    tag = get_object_or_404(models.Tag, id=id)
    return HttpResponse(tag.description)


def download_zip(request, format, slug=None):
    url = None
    if format in models.Book.ebook_formats:
        url = models.Book.zip_format(format)
    elif format in ('mp3', 'ogg') and slug is not None:
        book = get_object_or_404(models.Book, slug=slug)
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
        return get_object_or_404(models.Book, slug=slug)

    def context_description(self, request, obj):
        return obj.pretty_title()


####
# Includes
####


@ssi_included
def book_mini(request, pk, with_link=True):
    book = get_object_or_404(models.Book, pk=pk)
    author_str = ", ".join(tag.name
        for tag in book.tags.filter(category='author'))
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
    book = get_object_or_404(models.Book, pk=pk)
    stage_note, stage_note_url = book.stage_note()

    return render(request, 'catalogue/book_short.html', {
        'book': book,
        'has_audio': book.has_media('mp3'),
        'main_link': book.get_absolute_url(),
        'parents': book.parents(),
        'tags': split_tags(book.tags.exclude(category__in=('set', 'theme'))),
        'show_lang': book.language_code() != settings.LANGUAGE_CODE,
        'stage_note': stage_note,
        'stage_note_url': stage_note_url,
    })


@ssi_included(get_ssi_vars=lambda pk: book_short.get_ssi_vars(pk) +
    (lambda ipk: (
        ('social_tags.choose_cite', [ipk]),
        ('catalogue_tags.choose_fragment', [ipk], {
            'unless': V('social_tags.choose_cite', [ipk])}),
    ))(ssi_expect(pk, int)))
def book_wide(request, pk):
    book = get_object_or_404(models.Book, pk=pk)
    stage_note, stage_note_url = book.stage_note()
    extra_info = book.extra_info

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
        'themes': book.related_themes(),
    })


@ssi_included
def fragment_short(request, pk):
    fragment = get_object_or_404(models.Fragment, pk=pk)
    return render(request, 'catalogue/fragment_short.html',
        {'fragment': fragment})


@ssi_included
def fragment_promo(request, pk):
    fragment = get_object_or_404(models.Fragment, pk=pk)
    return render(request, 'catalogue/fragment_promo.html', {
        'fragment': fragment
    })
