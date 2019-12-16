# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from collections import OrderedDict
import random

from django.conf import settings
from django.http.response import HttpResponseForbidden
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponsePermanentRedirect
from django.urls import reverse
from django.db.models import Q, QuerySet
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.http import urlquote_plus
from django.utils import translation
from django.utils.translation import ugettext as _, ugettext_lazy
from django.views.decorators.cache import never_cache

from ajaxable.utils import AjaxableFormView
from club.models import Membership
from annoy.models import DynamicTextInsert
from pdcounter import views as pdcounter_views
from picture.models import Picture, PictureArea
from catalogue import constants
from catalogue import forms
from catalogue.helpers import get_top_level_related_tags
from catalogue.models import Book, Collection, Tag, Fragment
from catalogue.utils import split_tags
from catalogue.models.tag import prefetch_relations
from wolnelektury.utils import is_crawler

staff_required = user_passes_test(lambda user: user.is_staff)


def catalogue(request):
    return render(request, 'catalogue/catalogue.html', {
        'books': Book.objects.filter(parent=None),
        'pictures': Picture.objects.all(),
        'collections': Collection.objects.all(),
        'active_menu_item': 'all_works',
    })


def book_list(request, filters=None, template_name='catalogue/book_list.html',
              nav_template_name='catalogue/snippets/book_list_nav.html',
              list_template_name='catalogue/snippets/book_list.html'):
    """ generates a listing of all books, optionally filtered """
    books_by_author, orphans, books_by_parent = Book.book_list(filters)
    books_nav = OrderedDict()
    for tag in books_by_author:
        if books_by_author[tag]:
            books_nav.setdefault(tag.sort_key[0], []).append(tag)
    return render(request, template_name, {
        'rendered_nav': render_to_string(nav_template_name, {'books_nav': books_nav}),
        'rendered_book_list': render_to_string(list_template_name, {
            'books_by_author': books_by_author,
            'orphans': orphans,
            'books_by_parent': books_by_parent,
        })
    })


def daisy_list(request):
    return book_list(request, Q(media__type='daisy'), template_name='catalogue/daisy_list.html')


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
    return render(
        request,
        'catalogue/differentiate_tags.html',
        {'tags': tags, 'options': options, 'unparsed': ambiguous_slugs[1:]}
    )


def object_list(request, objects, fragments=None, related_tags=None, tags=None,
                list_type='books', extra=None):
    if not tags:
        tags = []
    tag_ids = [tag.pk for tag in tags]

    related_tag_lists = []
    if related_tags:
        related_tag_lists.append(related_tags)
    else:
        related_tag_lists.append(
            Tag.objects.usage_for_queryset(
                objects, counts=True
            ).exclude(category='set').exclude(pk__in=tag_ids))
    if not (extra and extra.get('theme_is_set')):
        if fragments is None:
            if list_type == 'gallery':
                fragments = PictureArea.objects.filter(picture__in=objects)
            else:
                fragments = Fragment.objects.filter(book__in=objects)
        related_tag_lists.append(
            Tag.objects.usage_for_queryset(
                fragments, counts=True
            ).filter(category='theme').exclude(pk__in=tag_ids)
            .only('name', 'sort_key', 'category', 'slug'))
        if isinstance(objects, QuerySet):
            objects = prefetch_relations(objects, 'author')

    categories = split_tags(*related_tag_lists)

    objects = list(objects)

    if not objects and len(tags) == 1 and list_type == 'books':
        if PictureArea.tagged.with_any(tags).exists() or Picture.tagged.with_any(tags).exists():
            return redirect('tagged_object_list_gallery', '/'.join(tag.url_chunk for tag in tags))

    if len(objects) > 3:
        best = random.sample(objects, 3)
    else:
        best = objects

    result = {
        'object_list': objects,
        'categories': categories,
        'list_type': list_type,
        'tags': tags,

        'formats_form': forms.DownloadFormatsForm(),
        'best': best,
        'active_menu_item': list_type,
    }
    if extra:
        result.update(extra)
    return render(
        request,
        'catalogue/tagged_object_list.html', result,
    )


def literature(request):
    books = Book.objects.filter(parent=None)
    return object_list(request, books, related_tags=get_top_level_related_tags([]))


def gallery(request):
    return object_list(request, Picture.objects.all(), list_type='gallery')


def audiobooks(request):
    audiobooks = Book.objects.filter(media__type__in=('mp3', 'ogg')).distinct()
    return object_list(request, audiobooks, list_type='audiobooks', extra={
        'daisy': Book.objects.filter(media__type='daisy').distinct(),
    })


class ResponseInstead(Exception):
    def __init__(self, response):
        super(ResponseInstead, self).__init__()
        self.response = response


def analyse_tags(request, tag_str):
    try:
        tags = Tag.get_tag_list(tag_str)
    except Tag.DoesNotExist:
        # Perhaps the user is asking about an author in Public Domain
        # counter (they are not represented in tags)
        chunks = tag_str.split('/')
        if len(chunks) == 2 and chunks[0] == 'autor':
            raise ResponseInstead(pdcounter_views.author_detail(request, chunks[1]))
        raise Http404
    except Tag.MultipleObjectsReturned as e:
        # Ask the user to disambiguate
        raise ResponseInstead(differentiate_tags(request, e.tags, e.ambiguous_slugs))
    except Tag.UrlDeprecationWarning as e:
        raise ResponseInstead(HttpResponsePermanentRedirect(
            reverse('tagged_object_list', args=['/'.join(tag.url_chunk for tag in e.tags)])))

    try:
        if len(tags) > settings.MAX_TAG_LIST:
            raise Http404
    except AttributeError:
        pass

    return tags


def theme_list(request, tags, list_type):
    shelf_tags = [tag for tag in tags if tag.category == 'set']
    fragment_tags = [tag for tag in tags if tag.category != 'set']
    if list_type == 'gallery':
        fragments = PictureArea.tagged.with_all(fragment_tags)
    else:
        fragments = Fragment.tagged.with_all(fragment_tags)

    if shelf_tags:
        # TODO: Pictures on shelves not supported yet.
        books = Book.tagged.with_all(shelf_tags).order_by()
        fragments = fragments.filter(Q(book__in=books) | Q(book__ancestor__in=books))

    if not fragments and len(tags) == 1 and list_type == 'books':
        if PictureArea.tagged.with_any(tags).exists() or Picture.tagged.with_any(tags).exists():
            return redirect('tagged_object_list_gallery', '/'.join(tag.url_chunk for tag in tags))

    return object_list(request, fragments, tags=tags, list_type=list_type, extra={
        'theme_is_set': True,
        'active_menu_item': 'theme',
    })


def tagged_object_list(request, tags, list_type):
    try:
        tags = analyse_tags(request, tags)
    except ResponseInstead as e:
        return e.response

    if is_crawler(request) and len(tags) > 1:
        return HttpResponseForbidden('address removed from crawling. check robots.txt')

    if list_type == 'gallery' and any(tag.category == 'set' for tag in tags):
        raise Http404

    if any(tag.category in ('theme', 'thing') for tag in tags):
        return theme_list(request, tags, list_type=list_type)

    if list_type == 'books':
        books = Book.tagged.with_all(tags)

        if any(tag.category == 'set' for tag in tags):
            params = {'objects': books}
        else:
            params = {
                'objects': Book.tagged_top_level(tags),
                'fragments': Fragment.objects.filter(book__in=books),
                'related_tags': get_top_level_related_tags(tags),
            }
    elif list_type == 'gallery':
        params = {'objects': Picture.tagged.with_all(tags)}
    elif list_type == 'audiobooks':
        audiobooks = Book.objects.filter(media__type__in=('mp3', 'ogg')).distinct()
        params = {
            'objects': Book.tagged.with_all(tags, audiobooks),
            'extra': {
                'daisy': Book.tagged.with_all(
                    tags, audiobooks.filter(media__type='daisy').distinct()
                ),
            }
        }
    else:
        raise Http404

    return object_list(request, tags=tags, list_type=list_type, **params)


def book_fragments(request, slug, theme_slug):
    book = get_object_or_404(Book, slug=slug)
    theme = get_object_or_404(Tag, slug=theme_slug, category='theme')
    fragments = Fragment.tagged.with_all([theme]).filter(
        Q(book=book) | Q(book__ancestor=book))

    return render(
        request,
        'catalogue/book_fragments.html',
        {
            'book': book,
            'theme': theme,
            'fragments': fragments,
            'active_menu_item': 'books',
        })


@never_cache
def book_detail(request, slug):
    try:
        book = Book.objects.get(slug=slug)
    except Book.DoesNotExist:
        return pdcounter_views.book_stub_detail(request, slug)

    return render(
        request,
        'catalogue/book_detail.html',
        {
            'book': book,
            'book_children': book.children.all().order_by('parent_number', 'sort_key'),
            'active_menu_item': 'books',
        })


# używane w publicznym interfejsie
def player(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if not book.has_media('mp3'):
        raise Http404

    audiobooks, projects = book.get_audiobooks()

    return render(
        request,
        'catalogue/player.html',
        {
            'book': book,
            'audiobook': '',
            'audiobooks': audiobooks,
            'projects': projects,
        })


def book_text(request, slug):
    book = get_object_or_404(Book, slug=slug)

    if book.preview and not Membership.is_active_for(request.user):
        return HttpResponseRedirect(book.get_absolute_url())

    if not book.has_html_file():
        raise Http404
    with book.html_file.open('r') as f:
        book_text = f.read()

    return render(request, 'catalogue/book_text.html', {
        'book': book,
        'book_text': book_text,
        'inserts': DynamicTextInsert.get_all(request)
    })


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
                _("An error occurred: %(exception)s\n\n%(tb)s") % {
                    'exception': exception, 'tb': tb
                },
                mimetype='text/plain'
            )
        return HttpResponse(_("Book imported successfully"))
    return HttpResponse(_("Error importing file: %r") % book_import_form.errors)


# info views for API

def book_info(request, book_id, lang='pl'):
    book = get_object_or_404(Book, id=book_id)
    # set language by hand
    translation.activate(lang)
    return render(request, 'catalogue/book_info.html', {'book': book})


def tag_info(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    return HttpResponse(tag.description)


@never_cache
def embargo_link(request, key, format_, slug):
    book = get_object_or_404(Book, slug=slug)
    if format_ not in Book.formats:
        raise Http404
    if key != book.preview_key:
        raise Http404
    media_file = book.get_media(format_)
    if not book.preview:
        return HttpResponseRedirect(media_file.url)
    return HttpResponse(media_file, content_type=constants.EBOOK_CONTENT_TYPES[format_])


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
    template = 'catalogue/custom_pdf_form.html'
    honeypot = True

    def __call__(self, *args, **kwargs):
        if settings.NO_CUSTOM_PDF:
            raise Http404('Custom PDF is disabled')
        return super(CustomPDFFormView, self).__call__(*args, **kwargs)

    def form_args(self, request, obj):
        """Override to parse view args and give additional args to the form."""
        return (obj,), {}

    def validate_object(self, obj, request):
        book = obj
        if book.preview and not Membership.is_active_for(request.user):
            return HttpResponseRedirect(book.get_absolute_url())
        return super(CustomPDFFormView, self).validate_object(obj, request)

    def get_object(self, request, slug, *args, **kwargs):
        book = get_object_or_404(Book, slug=slug)
        return book

    def context_description(self, request, obj):
        return obj.pretty_title()


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
        'active_menu_item': 'theme' if category == 'theme' else None,
    })


def collections(request):
    objects = Collection.objects.all()

    if len(objects) > 3:
        best = random.sample(list(objects), 3)
    else:
        best = objects

    return render(request, 'catalogue/collections.html', {
        'objects': objects,
        'best': best,
    })


def ridero_cover(request, slug):
    from librarian.cover import make_cover
    wldoc = Book.objects.get(slug=slug).wldocument()
    cover = make_cover(wldoc.book_info, width=980, bleed=20, format='PNG')
    response = HttpResponse(content_type="image/png")
    cover.save(response)
    return response


def get_isbn(request, book_format, slug):
    book = Book.objects.get(slug=slug)
    return HttpResponse(book.get_extra_info_json().get('isbn_%s' % book_format))
