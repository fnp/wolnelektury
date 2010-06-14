# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import tempfile
import zipfile
import sys
import pprint
import traceback
import re
import itertools
from operator import itemgetter 

from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.datastructures import SortedDict
from django.views.decorators.http import require_POST
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import simplejson
from django.utils.functional import Promise
from django.utils.encoding import force_unicode
from django.utils.http import urlquote_plus
from django.views.decorators import cache
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list

from catalogue import models
from catalogue import forms
from catalogue.utils import split_tags
from newtagging import views as newtagging_views


staff_required = user_passes_test(lambda user: user.is_staff)


class LazyEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return obj


def main_page(request):
    if request.user.is_authenticated():
        shelves = models.Tag.objects.filter(category='set', user=request.user)
        new_set_form = forms.NewSetForm()
    extra_where = "NOT catalogue_tag.category = 'set'"
    tags = models.Tag.objects.usage_for_model(models.Book, counts=True, extra={'where': [extra_where]})
    fragment_tags = models.Tag.objects.usage_for_model(models.Fragment, counts=True,
        extra={'where': ["catalogue_tag.category = 'theme'"] + [extra_where]})
    categories = split_tags(tags)

    form = forms.SearchForm()
    return render_to_response('catalogue/main_page.html', locals(),
        context_instance=RequestContext(request))


def book_list(request):
    books = models.Book.objects.all()
    form = forms.SearchForm()

    books_by_first_letter = SortedDict()
    for book in books:
        books_by_first_letter.setdefault(book.title[0], []).append(book)

    return render_to_response('catalogue/book_list.html', locals(),
        context_instance=RequestContext(request))


def differentiate_tags(request, tags, ambiguous_slugs):
    beginning = '/'.join(tag.url_chunk for tag in tags)
    unparsed = '/'.join(ambiguous_slugs[1:])
    options = []
    for tag in models.Tag.objects.exclude(category='book').filter(slug=ambiguous_slugs[0]):
        options.append({
            'url_args': '/'.join((beginning, tag.url_chunk, unparsed)).rstrip('/'),
            'tags': tags + [tag]
        })
    return render_to_response('catalogue/differentiate_tags.html',
                {'tags': tags, 'options': options, 'unparsed': unparsed}, 
                context_instance=RequestContext(request))


def tagged_object_list(request, tags=''):
    try:
        tags = models.Tag.get_tag_list(tags)
    except models.Tag.DoesNotExist:
        raise Http404
    except models.Tag.MultipleObjectsReturned, e:
        return differentiate_tags(request, e.tags, e.ambiguous_slugs)

    try:
        if len(tags) > settings.MAX_TAG_LIST:
            raise Http404
    except AttributeError:
        pass

    if len([tag for tag in tags if tag.category == 'book']):
        raise Http404

    theme_is_set = [tag for tag in tags if tag.category == 'theme']
    shelf_is_set = len(tags) == 1 and tags[0].category == 'set'
    my_shelf_is_set = shelf_is_set and request.user.is_authenticated() and request.user == tags[0].user

    objects = only_author = pd_counter = None
    categories = {}

    if theme_is_set:
        shelf_tags = [tag for tag in tags if tag.category == 'set']
        fragment_tags = [tag for tag in tags if tag.category != 'set']
        fragments = models.Fragment.tagged.with_all(fragment_tags)

        if shelf_tags:
            books = models.Book.tagged.with_all(shelf_tags).order_by()
            l_tags = [book.book_tag() for book in books]
            fragments = models.Fragment.tagged.with_any(l_tags, fragments)

        # newtagging goes crazy if we just try:
        #related_tags = models.Tag.objects.usage_for_queryset(fragments, counts=True, 
        #                    extra={'where': ["catalogue_tag.category != 'book'"]})
        fragment_keys = [fragment.pk for fragment in fragments]
        if fragment_keys:
            related_tags = models.Fragment.tags.usage(counts=True,
                                filters={'pk__in': fragment_keys},
                                extra={'where': ["catalogue_tag.category != 'book'"]})
            related_tags = (tag for tag in related_tags if tag not in fragment_tags)
            categories = split_tags(related_tags)

            objects = fragments
    else:
        # get relevant books and their tags
        objects = models.Book.tagged.with_all(tags).order_by()
        l_tags = [book.book_tag() for book in objects]
        # eliminate descendants
        descendants_keys = [book.pk for book in models.Book.tagged.with_any(l_tags)]
        if descendants_keys:
            objects = objects.exclude(pk__in=descendants_keys)
        
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
        pd_counter = only_author and tags[0].goes_to_pd()
        objects = models.Book.objects.none()

    return object_list(
        request,
        objects,
        template_name='catalogue/tagged_object_list.html',
        extra_context={
            'categories': categories,
            'shelf_is_set': shelf_is_set,
            'only_author': only_author,
            'pd_counter': pd_counter,
            'user_is_owner': my_shelf_is_set,
            'formats_form': forms.DownloadFormatsForm(),

            'tags': tags,
        }
    )


def book_fragments(request, book_slug, theme_slug):
    book = get_object_or_404(models.Book, slug=book_slug)
    book_tag = get_object_or_404(models.Tag, slug='l-' + book_slug, category='book')
    theme = get_object_or_404(models.Tag, slug=theme_slug, category='theme')
    fragments = models.Fragment.tagged.with_all([book_tag, theme])

    form = forms.SearchForm()
    return render_to_response('catalogue/book_fragments.html', locals(),
        context_instance=RequestContext(request))


def book_detail(request, slug):
    try:
        book = models.Book.objects.get(slug=slug)
    except models.Book.DoesNotExist:
        return book_stub_detail(request, slug)

    book_tag = book.book_tag()
    tags = list(book.tags.filter(~Q(category='set')))
    categories = split_tags(tags)
    book_children = book.children.all().order_by('parent_number')
    extra_where = "catalogue_tag.category = 'theme'"
    book_themes = models.Tag.objects.related_for_model(book_tag, models.Fragment, counts=True, extra={'where': [extra_where]})
    extra_info = book.get_extra_info_value()

    form = forms.SearchForm()
    return render_to_response('catalogue/book_detail.html', locals(),
        context_instance=RequestContext(request))


def book_stub_detail(request, slug):
    book = get_object_or_404(models.BookStub, slug=slug)
    pd_counter = book.pd
    form = forms.SearchForm()

    return render_to_response('catalogue/book_stub_detail.html', locals(),
        context_instance=RequestContext(request))


def book_text(request, slug):
    book = get_object_or_404(models.Book, slug=slug)
    book_themes = {}
    for fragment in book.fragments.all():
        for theme in fragment.tags.filter(category='theme'):
            book_themes.setdefault(theme, []).append(fragment)

    book_themes = book_themes.items()
    book_themes.sort(key=lambda s: s[0].sort_key)
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


def _sqlite_word_starts_with(name, prefix):
    """ version of _word_starts_with for SQLite 
    
    SQLite in Django uses Python re module
    """
    kwargs = {}
    prefix = _no_diacritics_regexp(unicode_re_escape(prefix))
    kwargs['%s__iregex' % name] = ur"(^|(?<=[^\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ]))%s" % prefix
    return Q(**kwargs)


if settings.DATABASE_ENGINE == 'sqlite3':
    _word_starts_with = _sqlite_word_starts_with


def _tags_starting_with(prefix, user=None):
    prefix = prefix.lower()
    book_stubs = models.BookStub.objects.filter(_word_starts_with('title', prefix))
    books = models.Book.objects.filter(_word_starts_with('title', prefix))
    book_stubs = filter(lambda x: x not in books, book_stubs)
    tags = models.Tag.objects.filter(_word_starts_with('name', prefix))
    if user and user.is_authenticated():
        tags = tags.filter(~Q(category='book') & (~Q(category='set') | Q(user=user)))
    else:
        tags = tags.filter(~Q(category='book') & ~Q(category='set'))

    return list(books) + list(tags) + list(book_stubs)


def _get_result_link(match, tag_list):
    if isinstance(match, models.Book) or isinstance(match, models.BookStub):
        return match.get_absolute_url()
    else:
        return reverse('catalogue.views.tagged_object_list',
            kwargs={'tags': '/'.join(tag.url_chunk for tag in tag_list + [match])}
        )

def _get_result_type(match):
    if isinstance(match, models.Book) or isinstance(match, models.BookStub):
        type = 'book'
    else:
        type = match.category
    return dict(models.TAG_CATEGORIES)[type]



def find_best_matches(query, user=None):
    """ Finds a Book, Tag or Bookstub best matching a query.
    
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
    exact_matches = tuple(res for res in result if res.name.lower() == query)
    if exact_matches:
        return exact_matches
    else:
        return result[:1]


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
        return render_to_response('catalogue/search_no_hits.html', {'tags':tag_list, 'prefix':prefix},
            context_instance=RequestContext(request))


def tags_starting_with(request):
    prefix = request.GET.get('q', '')
    # Prefix must have at least 2 characters
    if len(prefix) < 2:
        return HttpResponse('')

    return HttpResponse('\n'.join(tag.name for tag in _tags_starting_with(prefix, request.user)))


# ====================
# = Shelf management =
# ====================
@login_required
@cache.never_cache
def user_shelves(request):
    shelves = models.Tag.objects.filter(category='set', user=request.user)
    new_set_form = forms.NewSetForm()
    return render_to_response('catalogue/user_shelves.html', locals(),
            context_instance=RequestContext(request))

@cache.never_cache
def book_sets(request, slug):
    book = get_object_or_404(models.Book, slug=slug)
    user_sets = models.Tag.objects.filter(category='set', user=request.user)
    book_sets = book.tags.filter(category='set', user=request.user)

    if not request.user.is_authenticated():
        return HttpResponse(_('<p>To maintain your shelves you need to be logged in.</p>'))

    if request.method == 'POST':
        form = forms.ObjectSetsForm(book, request.user, request.POST)
        if form.is_valid():
            old_shelves = list(book.tags.filter(category='set'))
            new_shelves = [models.Tag.objects.get(pk=id) for id in form.cleaned_data['set_ids']]

            for shelf in [shelf for shelf in old_shelves if shelf not in new_shelves]:
                shelf.book_count -= 1
                shelf.save()

            for shelf in [shelf for shelf in new_shelves if shelf not in old_shelves]:
                shelf.book_count += 1
                shelf.save()

            book.tags = new_shelves + list(book.tags.filter(~Q(category='set') | ~Q(user=request.user)))
            if request.is_ajax():
                return HttpResponse(_('<p>Shelves were sucessfully saved.</p>'))
            else:
                return HttpResponseRedirect('/')
    else:
        form = forms.ObjectSetsForm(book, request.user)
        new_set_form = forms.NewSetForm()

    return render_to_response('catalogue/book_sets.html', locals(),
        context_instance=RequestContext(request))


@login_required
@require_POST
@cache.never_cache
def remove_from_shelf(request, shelf, book):
    book = get_object_or_404(models.Book, slug=book)
    shelf = get_object_or_404(models.Tag, slug=shelf, category='set', user=request.user)

    if shelf in book.tags:
        models.Tag.objects.remove_tag(book, shelf)

        shelf.book_count -= 1
        shelf.save()

        return HttpResponse(_('Book was successfully removed from the shelf'))
    else:
        return HttpResponse(_('This book is not on the shelf'))


def collect_books(books):
    """
    Returns all real books in collection.
    """
    result = []
    for book in books:
        if len(book.children.all()) == 0:
            result.append(book)
        else:
            result += collect_books(book.children.all())
    return result


@cache.never_cache
def download_shelf(request, slug):
    """"
    Create a ZIP archive on disk and transmit it in chunks of 8KB,
    without loading the whole file into memory. A similar approach can
    be used for large dynamic PDF files.                                        
    """
    shelf = get_object_or_404(models.Tag, slug=slug, category='set')

    formats = []
    form = forms.DownloadFormatsForm(request.GET)
    if form.is_valid():
        formats = form.cleaned_data['formats']
    if len(formats) == 0:
        formats = ['pdf', 'epub', 'odt', 'txt', 'mp3', 'ogg']

    # Create a ZIP archive
    temp = tempfile.TemporaryFile()
    archive = zipfile.ZipFile(temp, 'w')

    for book in collect_books(models.Book.tagged.with_all(shelf)):
        if 'pdf' in formats and book.pdf_file:
            filename = book.pdf_file.path
            archive.write(filename, str('%s.pdf' % book.slug))
        if 'epub' in formats and book.epub_file:
            filename = book.epub_file.path
            archive.write(filename, str('%s.epub' % book.slug))
        if 'odt' in formats and book.odt_file:
            filename = book.odt_file.path
            archive.write(filename, str('%s.odt' % book.slug))
        if 'txt' in formats and book.txt_file:
            filename = book.txt_file.path
            archive.write(filename, str('%s.txt' % book.slug))
        if 'mp3' in formats and book.mp3_file:
            filename = book.mp3_file.path
            archive.write(filename, str('%s.mp3' % book.slug))
        if 'ogg' in formats and book.ogg_file:
            filename = book.ogg_file.path
            archive.write(filename, str('%s.ogg' % book.slug))
    archive.close()

    response = HttpResponse(content_type='application/zip', mimetype='application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % shelf.sort_key
    response['Content-Length'] = temp.tell()

    temp.seek(0)
    response.write(temp.read())
    return response


@cache.never_cache
def shelf_book_formats(request, shelf):
    """"
    Returns a list of formats of books in shelf.
    """
    shelf = get_object_or_404(models.Tag, slug=shelf, category='set')

    formats = {'pdf': False, 'epub': False, 'odt': False, 'txt': False, 'mp3': False, 'ogg': False}

    for book in collect_books(models.Book.tagged.with_all(shelf)):
        if book.pdf_file:
            formats['pdf'] = True
        if book.epub_file:
            formats['epub'] = True
        if book.odt_file:
            formats['odt'] = True
        if book.txt_file:
            formats['txt'] = True
        if book.mp3_file:
            formats['mp3'] = True
        if book.ogg_file:
            formats['ogg'] = True

    return HttpResponse(LazyEncoder().encode(formats))


@login_required
@require_POST
@cache.never_cache
def new_set(request):
    new_set_form = forms.NewSetForm(request.POST)
    if new_set_form.is_valid():
        new_set = new_set_form.save(request.user)

        if request.is_ajax():
            return HttpResponse(_('<p>Shelf <strong>%s</strong> was successfully created</p>') % new_set)
        else:
            return HttpResponseRedirect('/')

    return HttpResponseRedirect('/')


@login_required
@require_POST
@cache.never_cache
def delete_shelf(request, slug):
    user_set = get_object_or_404(models.Tag, slug=slug, category='set', user=request.user)
    user_set.delete()

    if request.is_ajax():
        return HttpResponse(_('<p>Shelf <strong>%s</strong> was successfully removed</p>') % user_set.name)
    else:
        return HttpResponseRedirect('/')


# ==================
# = Authentication =
# ==================
@require_POST
@cache.never_cache
def login(request):
    form = AuthenticationForm(data=request.POST, prefix='login')
    if form.is_valid():
        auth.login(request, form.get_user())
        response_data = {'success': True, 'errors': {}}
    else:
        response_data = {'success': False, 'errors': form.errors}
    return HttpResponse(LazyEncoder(ensure_ascii=False).encode(response_data))


@require_POST
@cache.never_cache
def register(request):
    registration_form = UserCreationForm(request.POST, prefix='registration')
    if registration_form.is_valid():
        user = registration_form.save()
        user = auth.authenticate(
            username=registration_form.cleaned_data['username'],
            password=registration_form.cleaned_data['password1']
        )
        auth.login(request, user)
        response_data = {'success': True, 'errors': {}}
    else:
        response_data = {'success': False, 'errors': registration_form.errors}
    return HttpResponse(LazyEncoder(ensure_ascii=False).encode(response_data))


@cache.never_cache
def logout_then_redirect(request):
    auth.logout(request)
    return HttpResponseRedirect(urlquote_plus(request.GET.get('next', '/'), safe='/?='))



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
            info = sys.exc_info()
            exception = pprint.pformat(info[1])
            tb = '\n'.join(traceback.format_tb(info[2]))
            _('Today is %(month)s, %(day)s.') % {'month': m, 'day': d}
            return HttpResponse(_("An error occurred: %(exception)s\n\n%(tb)s") % {'exception':exception, 'tb':tb}, mimetype='text/plain')
        return HttpResponse(_("Book imported successfully"))
    else:
        return HttpResponse(_("Error importing file: %r") % book_import_form.errors)



def clock(request):
    """ Provides server time for jquery.countdown,
    in a format suitable for Date.parse()
    """
    from datetime import datetime
    return HttpResponse(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
