# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import re
import itertools

from django.conf import settings
from django.core.cache import get_cache
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponsePermanentRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.datastructures import SortedDict
from django.utils.http import urlquote_plus
from django.utils import translation
from django.utils.translation import get_language, ugettext as _, ugettext_lazy
from django.views.decorators.vary import vary_on_headers

from ajaxable.utils import JSONResponse, AjaxableFormView
from catalogue import models
from catalogue import forms
from catalogue.utils import split_tags, MultiQuerySet
from catalogue.templatetags.catalogue_tags import tag_list, collection_list
from pdcounter import models as pdcounter_models
from pdcounter import views as pdcounter_views
from suggest.forms import PublishingSuggestForm
from picture.models import Picture

staff_required = user_passes_test(lambda user: user.is_staff)
permanent_cache = get_cache('permanent')


@vary_on_headers('X-Requested-With')
def catalogue(request):
    cache_key='catalogue.catalogue/' + get_language()
    output = permanent_cache.get(cache_key)
    if output is None:
        tags = models.Tag.objects.exclude(
            category__in=('set', 'book')).exclude(book_count=0)
        tags = list(tags)
        for tag in tags:
            tag.count = tag.book_count
        categories = split_tags(tags)
        fragment_tags = categories.get('theme', [])
        collections = models.Collection.objects.all()
        render_tag_list = lambda x: render_to_string(
            'catalogue/tag_list.html', tag_list(x))
        output = {'theme': render_tag_list(fragment_tags)}
        for category, tags in categories.items():
            output[category] = render_tag_list(tags)
        output['collections'] = render_to_string(
            'catalogue/collection_list.html', collection_list(collections))
        permanent_cache.set(cache_key, output)
    if request.is_ajax():
        return JSONResponse(output)
    else:
        return render_to_response('catalogue/catalogue.html', locals(),
            context_instance=RequestContext(request))


def book_list(request, filter=None, get_filter=None,
        template_name='catalogue/book_list.html',
        nav_template_name='catalogue/snippets/book_list_nav.html',
        list_template_name='catalogue/snippets/book_list.html',
        cache_key='catalogue.book_list',
        context=None,
        ):
    """ generates a listing of all books, optionally filtered with a test function """
    cache_key = "%s/%s" % (cache_key, get_language())
    cached = permanent_cache.get(cache_key)
    if cached is not None:
        rendered_nav, rendered_book_list = cached
    else:
        if get_filter:
            filter = get_filter()
        books_by_author, orphans, books_by_parent = models.Book.book_list(filter)
        books_nav = SortedDict()
        for tag in books_by_author:
            if books_by_author[tag]:
                books_nav.setdefault(tag.sort_key[0], []).append(tag)
        rendered_nav = render_to_string(nav_template_name, locals())
        rendered_book_list = render_to_string(list_template_name, locals())
        permanent_cache.set(cache_key, (rendered_nav, rendered_book_list))
    return render_to_response(template_name, locals(),
        context_instance=RequestContext(request))


def audiobook_list(request):
    return book_list(request, Q(media__type='mp3') | Q(media__type='ogg'),
                     template_name='catalogue/audiobook_list.html',
                     list_template_name='catalogue/snippets/audiobook_list.html',
                     cache_key='catalogue.audiobook_list')


def daisy_list(request):
    return book_list(request, Q(media__type='daisy'),
                     template_name='catalogue/daisy_list.html',
                     cache_key='catalogue.daisy_list')


def collection(request, slug):
    coll = get_object_or_404(models.Collection, slug=slug)
    return book_list(request, get_filter=coll.get_query,
                     template_name='catalogue/collection.html',
                     cache_key='catalogue.collection:%s' % coll.slug,
                     context={'collection': coll})


def differentiate_tags(request, tags, ambiguous_slugs):
    beginning = '/'.join(tag.url_chunk for tag in tags)
    unparsed = '/'.join(ambiguous_slugs[1:])
    options = []
    for tag in models.Tag.objects.exclude(category='book').filter(slug=ambiguous_slugs[0]):
        options.append({
            'url_args': '/'.join((beginning, tag.url_chunk, unparsed)).strip('/'),
            'tags': [tag]
        })
    return render_to_response('catalogue/differentiate_tags.html',
                {'tags': tags, 'options': options, 'unparsed': ambiguous_slugs[1:]},
                context_instance=RequestContext(request))


def tagged_object_list(request, tags=''):
    try:
        tags = models.Tag.get_tag_list(tags)
    except models.Tag.DoesNotExist:
        chunks = tags.split('/')
        if len(chunks) == 2 and chunks[0] == 'autor':
            return pdcounter_views.author_detail(request, chunks[1])
        else:
            raise Http404
    except models.Tag.MultipleObjectsReturned, e:
        return differentiate_tags(request, e.tags, e.ambiguous_slugs)
    except models.Tag.UrlDeprecationWarning, e:
        return HttpResponsePermanentRedirect(reverse('tagged_object_list', args=['/'.join(tag.url_chunk for tag in e.tags)]))

    try:
        if len(tags) > settings.MAX_TAG_LIST:
            raise Http404
    except AttributeError:
        pass

    if len([tag for tag in tags if tag.category == 'book']):
        raise Http404

    theme_is_set = [tag for tag in tags if tag.category == 'theme']
    shelf_is_set = [tag for tag in tags if tag.category == 'set']
    only_shelf = shelf_is_set and len(tags) == 1
    only_my_shelf = only_shelf and request.user.is_authenticated() and request.user == tags[0].user

    objects = only_author = None
    categories = {}

    if theme_is_set:
        shelf_tags = [tag for tag in tags if tag.category == 'set']
        fragment_tags = [tag for tag in tags if tag.category != 'set']
        fragments = models.Fragment.tagged.with_all(fragment_tags)

        if shelf_tags:
            books = models.Book.tagged.with_all(shelf_tags).order_by()
            l_tags = models.Tag.objects.filter(category='book',
                slug__in=[book.book_tag_slug() for book in books.iterator()])
            fragments = models.Fragment.tagged.with_any(l_tags, fragments)

        # newtagging goes crazy if we just try:
        #related_tags = models.Tag.objects.usage_for_queryset(fragments, counts=True,
        #                    extra={'where': ["catalogue_tag.category != 'book'"]})
        fragment_keys = [fragment.pk for fragment in fragments.iterator()]
        if fragment_keys:
            related_tags = models.Fragment.tags.usage(counts=True,
                                filters={'pk__in': fragment_keys},
                                extra={'where': ["catalogue_tag.category != 'book'"]})
            related_tags = (tag for tag in related_tags if tag not in fragment_tags)
            categories = split_tags(related_tags)

            objects = fragments
    else:
        if shelf_is_set:
            objects = models.Book.tagged.with_all(tags)
        else:
            objects = models.Book.tagged_top_level(tags)

        # get related tags from `tag_counter` and `theme_counter`
        related_counts = {}
        tags_pks = [tag.pk for tag in tags]
        for book in objects:
            for tag_pk, value in itertools.chain(book.tag_counter.iteritems(), book.theme_counter.iteritems()):
                if tag_pk in tags_pks:
                    continue
                related_counts[tag_pk] = related_counts.get(tag_pk, 0) + value
        related_tags = models.Tag.objects.filter(pk__in=related_counts.keys())
        related_tags = [tag for tag in related_tags if tag not in tags]
        for tag in related_tags:
            tag.count = related_counts[tag.pk]

        categories = split_tags(related_tags)
        del related_tags

    if not objects:
        only_author = len(tags) == 1 and tags[0].category == 'author'
        objects = models.Book.objects.none()

    # Add pictures
    objects = MultiQuerySet(Picture.tagged.with_all(tags), objects)

    return render_to_response('catalogue/tagged_object_list.html',
        {
            'object_list': objects,
            'categories': categories,
            'only_shelf': only_shelf,
            'only_author': only_author,
            'only_my_shelf': only_my_shelf,
            'formats_form': forms.DownloadFormatsForm(),
            'tags': tags,
            'theme_is_set': theme_is_set,
        },
        context_instance=RequestContext(request))


def book_fragments(request, slug, theme_slug):
    book = get_object_or_404(models.Book, slug=slug)

    book_tag = book.book_tag()
    theme = get_object_or_404(models.Tag, slug=theme_slug, category='theme')
    fragments = models.Fragment.tagged.with_all([book_tag, theme])

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
    related = book.related_info()
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
    return re.sub('(?u)(\W)', r'\\\1', query)

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
        tags = tags.filter(~Q(category='book') & (~Q(category='set') | Q(user=user)))
    else:
        tags = tags.filter(~Q(category='book') & ~Q(category='set'))

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
        type = 'book'
    else:
        type = match.category
    return type


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
                  if isinstance(match, models.Tag) and match.category=='author')
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
    return JSONResponse(result, callback)


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
