# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from collections import OrderedDict
import random
import re
from urllib.parse import quote_plus

from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponsePermanentRedirect
from django.urls import reverse
from django.db.models import Q, QuerySet
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import translation
from django.utils.translation import gettext as _, gettext_lazy
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from ajaxable.utils import AjaxableFormView
from club.forms import ScheduleForm, DonationStep1Form
from club.models import Club
from annoy.models import DynamicTextInsert
from pdcounter import views as pdcounter_views
from picture.models import Picture, PictureArea
from wolnelektury.utils import is_ajax
from catalogue import constants
from catalogue import forms
from catalogue.helpers import get_top_level_related_tags
from catalogue.models import Book, Collection, Tag, Fragment
from catalogue.models.tag import TagRelation
from catalogue.utils import split_tags
from catalogue.models.tag import prefetch_relations

staff_required = user_passes_test(lambda user: user.is_staff)


def catalogue(request):
    return render(request, 'catalogue/catalogue.html', {
        'books': Book.objects.filter(findable=True, parent=None),
        'pictures': Picture.objects.all(),
        'collections': Collection.objects.filter(listed=True),
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
    if request.EXPERIMENTS['layout'].value:
        return object_list(request, Book.objects.filter(media__type='daisy'))
    return book_list(request, Q(media__type='daisy'), template_name='catalogue/daisy_list.html')


def collection(request, slug):
    coll = get_object_or_404(Collection, slug=slug)
    if request.EXPERIMENTS['layout'].value:
        template_name = 'catalogue/2022/collection.html'
    else:
        template_name = 'catalogue/collection.html'
    return render(request, template_name, {
        'collection': coll,
        'active_menu_item': 'collections',
    })


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


from django.db.models import FilteredRelation, Q
from django.views.decorators.cache import cache_control
from django.views.decorators.vary import vary_on_headers
from django.utils.decorators import method_decorator


@method_decorator([
    vary_on_headers('X-Requested-With'),
    cache_control(max_age=1),
], 'dispatch')
class ObjectListView(TemplateView):
    page_size = 100
    themed_page_size = 10
    item_template_name = ''
    orderings = {}
    default_ordering = None

    def analyse(self):
        self.is_themed = False
        self.ctx = ctx = {}
        ctx['tags'] = []        

    def dispatch(self, *args, **kwargs):
        try:
            self.analyse()
        except ResponseInstead as e:
            return e.response
        return super().dispatch(*args, **kwargs)
        
    def get_orderings(self):
        order = self.get_order()
        return [
            {
                "slug": k,
                "name": v[1],
                "active": k == order,
                "default": v[0] is None,
            }
            for k, v in self.orderings.items()
        ]

    def get_order(self):
        order = self.request.GET.get('order')
        if order not in self.orderings:
            order = self.default_ordering
        return order

    def order(self, qs):
        order_tag = self.get_order()
        if order_tag:
            order = self.orderings[order_tag]
            order_by = order[0]
            if order_by:
                qs = qs.order_by(order_by)
        return qs

    def search(self, qs):
        return qs

    def get_template_names(self):
        if is_ajax(self.request) or self.request.GET.get('dyn'):
            if self.is_themed:
                return self.dynamic_themed_template_name
            else:
                return self.dynamic_template_name
        else:
            if self.is_themed:
                return self.themed_template_name
            else:
                return self.template_name

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        ctx.update(self.ctx)
        qs = self.get_queryset()
        qs = self.search(qs)
        qs = self.order(qs)

        ctx['object_list'] = qs
        ctx['suggested_tags'] = self.get_suggested_tags(qs)
        ctx['suggested_tags_by_category'] = split_tags(ctx['suggested_tags'])
        return ctx


class BookList(ObjectListView):
    title = gettext_lazy('Literature')
    list_type = 'books'
    template_name = 'catalogue/2022/book_list.html'
    dynamic_template_name = 'catalogue/2022/dynamic_book_list.html'
    themed_template_name = 'catalogue/2022/themed_book_list.html'
    dynamic_themed_template_name = 'catalogue/2022/dynamic_themed_book_list.html'

    orderings = {
        'pop': ('-popularity__count', 'najpopularniejsze'),
        'alpha': (None, 'alfabetycznie'),
    }
    default_ordering = 'alpha'

    def get_queryset(self):
        return Book.objects.filter(parent=None, findable=True)

    def search(self, qs):
        term = self.request.GET.get('search')
        if term:
            meta_rels = TagRelation.objects.exclude(tag__category='set')
            # TODO: search tags in currently displaying language
            if self.is_themed:
                #qs = qs.annotate(
                #    meta=FilteredRelation('book__tag_relations', condition=Q(tag_relations__in=meta_rels))
                #)
                qs = qs.filter(
                    Q(book__title__icontains=term) |
                    #Q(meta__tag_relations__tag__name_pl__icontains=term) |
                    Q(text__icontains=term)
                ).distinct()
            else:
                qs = qs.annotate(
                    meta=FilteredRelation('tag_relations', condition=Q(tag_relations__in=meta_rels))
                )
                qs = qs.filter(Q(title__icontains=term) | Q(meta__tag__name_pl__icontains=term)).distinct()
        return qs


class ArtList(ObjectListView):
    template_name = 'catalogue/2022/book_list.html'
    dynamic_template_name = 'catalogue/2022/dynamic_book_list.html'
    title = gettext_lazy('Art')
    list_type = 'gallery'

    def get_queryset(self):
        return Picture.objects.all()

    def search(self, qs):
        term = self.request.GET.get('search')
        if term:
            qs = qs.filter(Q(title__icontains=term) | Q(tag_relations__tag__name_pl__icontains=term)).distinct()
        return qs
    

class LiteratureView(BookList):
    def get_suggested_tags(self, queryset):
        tags = list(get_top_level_related_tags([]))
        tags.sort(key=lambda t: -t.count)
        if self.request.user.is_authenticated:
            tags.extend(list(Tag.objects.filter(user=self.request.user).exclude(name='')))
        return tags


class AudiobooksView(LiteratureView):
    title = gettext_lazy('Audiobooks')
    list_type = 'audiobooks'

    def get_queryset(self):
        return Book.objects.filter(findable=True, media__type='mp3').distinct()


class GalleryView(ArtList):
    def get_suggested_tags(self, queryset):
        return Tag.objects.usage_for_queryset(
            queryset,
            counts=True
        ).exclude(pk__in=[t.id for t in self.ctx['tags']]).order_by('-count')
    

class TaggedObjectList(BookList):
    def analyse(self):
        super().analyse()
        self.ctx['tags'] = analyse_tags(self.request, self.kwargs['tags'])
        self.ctx['fragment_tags'] = [t for t in self.ctx['tags'] if t.category in ('theme', 'object')]
        self.ctx['work_tags'] = [t for t in self.ctx['tags'] if t not in self.ctx['fragment_tags']]
        self.is_themed = self.ctx['has_theme'] = bool(self.ctx['fragment_tags'])
        if self.is_themed:
            self.ctx['main_tag'] = self.ctx['fragment_tags'][0]
        elif self.ctx['tags']:
            self.ctx['main_tag'] = self.ctx['tags'][0]
        else:
            self.ctx['main_tag'] = None
        self.ctx['filtering_tags'] = [
            t for t in self.ctx['tags']
            if t is not self.ctx['main_tag']
        ]

    def get_queryset(self):
        qs = Book.tagged.with_all(self.ctx['work_tags']).filter(findable=True)
        qs = qs.exclude(ancestor__in=qs)
        if self.is_themed:
            fqs = Fragment.tagged.with_all(self.ctx['fragment_tags'])
            if self.ctx['work_tags']:
                fqs = fqs.filter(
                    Q(book__in=qs) | Q(book__ancestor__in=qs)
                )
            qs = fqs
        return qs

    def get_suggested_tags(self, queryset):
        tag_ids = [t.id for t in self.ctx['tags']]
        related_tags = list(get_top_level_related_tags(self.ctx['tags']))
        if not self.is_themed:
            if self.request.user.is_authenticated:
                qs = Book.tagged.with_all(self.ctx['tags']).filter(findable=True)
                related_tags.extend(list(
                    Tag.objects.usage_for_queryset(
                        qs
                    ).filter(
                        user=self.request.user
                    ).exclude(name='').exclude(pk__in=tag_ids)
                ))

            fragments = Fragment.objects.filter(
                Q(book__in=queryset) | Q(book__ancestor__in=queryset)
            )
            related_tags.extend(
                Tag.objects.usage_for_queryset(
                    fragments, counts=True
                ).filter(category__in=('theme', 'object')).exclude(pk__in=tag_ids)
            .only('name', 'sort_key', 'category', 'slug'))

        return related_tags

    
    
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
        if request.user.is_authenticated:
            related_tag_lists.append(
                Tag.objects.usage_for_queryset(
                    objects, counts=True
                ).filter(
                    user=request.user
                ).exclude(name='').exclude(pk__in=tag_ids)
            )
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
    suggest = []
    for c in ['set', 'author', 'epoch', 'kind', 'genre']:
        suggest.extend(sorted(categories[c], key=lambda t: -t.count))

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
        'suggest': suggest,
        'list_type': list_type,
        'tags': tags,
        'main_tag': tags[0] if tags else None,

        'formats_form': forms.DownloadFormatsForm(),
        'best': best,
        'active_menu_item': list_type,
    }
    if extra:
        result.update(extra)

    if request.EXPERIMENTS['layout'].value:
        has_theme = any(((theme := x).category == 'theme' for x in tags))
        if has_theme:
            result['main_tag'] = theme
            template = 'catalogue/2022/theme_detail.html'
        else:
            template = 'catalogue/2022/author_detail.html'
    else:
        template = 'catalogue/tagged_object_list.html'
        
    return render(
        request, template, result,
    )


def literature(request):
    if request.EXPERIMENTS['layout'].value:
        return LiteratureView.as_view()(request)
    books = Book.objects.filter(parent=None, findable=True)
    return object_list(request, books, related_tags=get_top_level_related_tags([]))


def gallery(request):
    if request.EXPERIMENTS['layout'].value:
        return GalleryView.as_view()(request)
    return object_list(request, Picture.objects.all(), list_type='gallery')


def audiobooks(request):
    if request.EXPERIMENTS['layout'].value:
        return AudiobooksView.as_view()(request)
    audiobooks = Book.objects.filter(findable=True, media__type__in=('mp3', 'ogg')).distinct()
    return object_list(request, audiobooks, list_type='audiobooks', extra={
        'daisy': Book.objects.filter(findable=True, media__type='daisy').distinct(),
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

    if not tags:
        raise Http404
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
    elif list_type == 'books':
        fragments = fragments.filter(book__findable=True)

    if not fragments and len(tags) == 1 and list_type == 'books':
        if PictureArea.tagged.with_any(tags).exists() or Picture.tagged.with_any(tags).exists():
            return redirect('tagged_object_list_gallery', '/'.join(tag.url_chunk for tag in tags))

    return object_list(request, fragments, tags=tags, list_type=list_type, extra={
        'theme_is_set': True,
        'active_menu_item': 'theme',
    })


def tagged_object_list(request, tags, list_type):
    if request.EXPERIMENTS['layout'].value and list_type in ('books', 'audiobooks'):
        return TaggedObjectList.as_view()(request, tags=tags)

    try:
        tags = analyse_tags(request, tags)
    except ResponseInstead as e:
        return e.response

    if list_type == 'gallery' and any(tag.category == 'set' for tag in tags):
        raise Http404

    if any(tag.category in ('theme', 'thing') for tag in tags):
        return theme_list(request, tags, list_type=list_type)

    if list_type == 'books':
        books = Book.tagged.with_all(tags)

        if any(tag.category == 'set' for tag in tags):
            params = {'objects': books}
        else:
            books = books.filter(findable=True)
            params = {
                'objects': Book.tagged_top_level(tags).filter(findable=True),
                'fragments': Fragment.objects.filter(book__in=books),
                'related_tags': get_top_level_related_tags(tags),
            }
    elif list_type == 'gallery':
        params = {'objects': Picture.tagged.with_all(tags)}
    elif list_type == 'audiobooks':
        audiobooks = Book.objects.filter(findable=True, media__type__in=('mp3', 'ogg')).distinct()
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

    if request.EXPERIMENTS['layout'].value:
        template_name = 'catalogue/2022/book_fragments.html'
    else:
        template_name = 'catalogue/book_fragments.html'
    
    return render(
        request,
        template_name,
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

    new_layout = request.EXPERIMENTS['layout']
    
    return render(
        request,
        'catalogue/2022/book_detail.html' if new_layout.value else 'catalogue/book_detail.html',
        {
            'book': book,
            'accessible': book.is_accessible_to(request.user),
            'book_children': book.children.all().order_by('parent_number', 'sort_key'),
            'active_menu_item': 'books',
            'club_form': ScheduleForm() if book.preview else None,
            'club': Club.objects.first() if book.preview else None,
            'donation_form': DonationStep1Form(),
        })


# używane w publicznym interfejsie
def player(request, slug):
    book = get_object_or_404(Book, slug=slug)
    if not book.has_media('mp3'):
        raise Http404

    audiobooks, projects, total_duration = book.get_audiobooks()

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

    if not book.is_accessible_to(request.user):
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
                content_type='text/plain'
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


def download_zip(request, file_format=None, media_format=None, slug=None):
    if file_format:
        url = Book.zip_format(file_format)
    elif media_format and slug is not None:
        book = get_object_or_404(Book, slug=slug)
        url = book.zip_audiobooks(media_format)
    else:
        raise Http404('No format specified for zip package')
    return HttpResponseRedirect(quote_plus(settings.MEDIA_URL + url, safe='/?='))


class CustomPDFFormView(AjaxableFormView):
    form_class = forms.CustomPDFForm
    title = gettext_lazy('Download custom PDF')
    submit = gettext_lazy('Download')
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
        if not book.is_accessible_to(request.user):
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

    if request.EXPERIMENTS['layout'].value:
        template_name = 'catalogue/2022/tag_catalogue.html'
    else:
        template_name = 'catalogue/tag_catalogue.html'

    return render(request, template_name, {
        'tags': tags,
        'best': best,
        'title': constants.CATEGORIES_NAME_PLURAL[category],
        'whole_category': constants.WHOLE_CATEGORY[category],
        'active_menu_item': 'theme' if category == 'theme' else None,
    })


def collections(request):
    objects = Collection.objects.filter(listed=True)

    if len(objects) > 3:
        best = random.sample(list(objects), 4)
    else:
        best = objects

    if request.EXPERIMENTS['layout'].value:
        template_name = 'catalogue/2022/collections.html'
    else:
        template_name = 'catalogue/collections.html'

    return render(request, template_name, {
        'objects': objects,
        'best': best,
        'active_menu_item': 'collections'
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
