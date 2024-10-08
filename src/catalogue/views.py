# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
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
from django.utils.translation import gettext_lazy
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

from ajaxable.utils import AjaxableFormView
from club.forms import DonationStep1Form
from club.models import Club
from annoy.models import DynamicTextInsert
from pdcounter import views as pdcounter_views
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
        'collections': Collection.objects.filter(listed=True),
    })


def daisy_list(request):
    return object_list(request, Book.objects.filter(media__type='daisy'))


def collection(request, slug):
    coll = get_object_or_404(Collection, slug=slug)
    template_name = 'catalogue/collection.html'
    return render(request, template_name, {
        'collection': coll,
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
    title = gettext_lazy('Literatura')
    list_type = 'books'
    template_name = 'catalogue/book_list.html'
    dynamic_template_name = 'catalogue/dynamic_book_list.html'
    themed_template_name = 'catalogue/themed_book_list.html'
    dynamic_themed_template_name = 'catalogue/dynamic_themed_book_list.html'

    orderings = {
        'pop': ('-popularity__count', gettext_lazy('najpopularniejsze')),
        'alpha': (None, gettext_lazy('alfabetycznie')),
    }
    default_ordering = 'alpha'

    def get_queryset(self):
        return Book.objects.filter(parent=None, findable=True)

    def search(self, qs):
        term = self.request.GET.get('search')
        if term:
            meta_rels = TagRelation.objects.filter(tag__category='author')
            # TODO: search tags in currently displaying language
            if self.is_themed:
                rels = meta_rels.filter(tag__name_pl__icontains=term)
                qs = qs.filter(
                    Q(book__title__icontains=term) |
                    Q(tag_relations__in=rels) |
                    Q(text__icontains=term)
                ).distinct()
            else:
                qs = qs.annotate(
                    meta=FilteredRelation('tag_relations', condition=Q(tag_relations__in=meta_rels))
                )
                qs = qs.filter(Q(title__icontains=term) | Q(meta__tag__name_pl__icontains=term)).distinct()
        return qs


class LiteratureView(BookList):
    def get_suggested_tags(self, queryset):
        tags = list(get_top_level_related_tags([]))
        tags.sort(key=lambda t: -t.count)
        if self.request.user.is_authenticated:
            tags.extend(list(Tag.objects.filter(user=self.request.user).exclude(name='')))
        return tags


class AudiobooksView(LiteratureView):
    title = gettext_lazy('Audiobooki')
    list_type = 'audiobooks'

    def get_queryset(self):
        return Book.objects.filter(findable=True, media__type='mp3').distinct()


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
        if len(self.ctx['tags']) == 1 and self.ctx['main_tag'].category == 'author':
            self.ctx['translation_list'] = self.ctx['main_tag'].book_set.all()

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
        if self.is_themed:
            related_tags = []
            current_books = self.get_queryset().values_list('book', flat=True).distinct()
            containing_books = Book.objects.filter(Q(id__in=current_books) | Q(children__in=current_books))

            related_tags.extend(list(
                Tag.objects.usage_for_queryset(
                    containing_books,
                ).exclude(category='set').exclude(pk__in=tag_ids)
            ))
            if self.request.user.is_authenticated:
                related_tags.extend(list(
                    Tag.objects.usage_for_queryset(
                        containing_books
                    ).filter(
                        user=self.request.user
                    ).exclude(name='').exclude(pk__in=tag_ids)
                ))
        else:
            related_tags = list(get_top_level_related_tags(self.ctx['tags']))
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

    
    
def object_list(request, objects, list_type='books'):
    related_tag_lists = []
    if True:
        related_tag_lists.append(
            Tag.objects.usage_for_queryset(
                objects, counts=True
            ).exclude(category='set'))
        if request.user.is_authenticated:
            related_tag_lists.append(
                Tag.objects.usage_for_queryset(
                    objects, counts=True
                ).filter(
                    user=request.user
                ).exclude(name='')
            )
    if True:
        fragments = Fragment.objects.filter(book__in=objects)
        related_tag_lists.append(
            Tag.objects.usage_for_queryset(
                fragments, counts=True
            ).filter(category='theme')
            .only('name', 'sort_key', 'category', 'slug'))
        if isinstance(objects, QuerySet):
            objects = prefetch_relations(objects, 'author')
    
    categories = split_tags(*related_tag_lists)
    suggest = []
    for c in ['set', 'author', 'epoch', 'kind', 'genre']:
        suggest.extend(sorted(categories[c], key=lambda t: -t.count))

    objects = list(objects)

    result = {
        'object_list': objects,
        'suggest': suggest,
        'list_type': list_type,
    }

    template = 'catalogue/author_detail.html'
        
    return render(
        request, template, result,
    )


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


def tagged_object_list(request, tags, list_type):
    return TaggedObjectList.as_view()(request, tags=tags)


def book_fragments(request, slug, theme_slug):
    book = get_object_or_404(Book, slug=slug)
    theme = get_object_or_404(Tag, slug=theme_slug, category='theme')
    fragments = Fragment.tagged.with_all([theme]).filter(
        Q(book=book) | Q(book__ancestor=book))

    template_name = 'catalogue/book_fragments.html'
    return render(
        request,
        template_name,
        {
            'book': book,
            'theme': theme,
            'fragments': fragments,
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
            'accessible': book.is_accessible_to(request.user),
            'book_children': book.children.all().order_by('parent_number', 'sort_key'),
            'club': Club.objects.first() if book.preview else None,
            'donation_form': DonationStep1Form(),
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
        'extra_info': book.get_extra_info_json(),
        'book_text': book_text,
        'inserts': DynamicTextInsert.get_all(request),

        'club': Club.objects.first(),
        'donation_form': DonationStep1Form(),
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
                "Błąd: %(exception)s\n\n%(tb)s" % {
                    'exception': exception, 'tb': tb
                },
                content_type='text/plain'
            )
        return HttpResponse("Książka zaimportowana")
    return HttpResponse("Błąd podczas importowania pliku: %r" % book_import_form.errors)


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
    title = gettext_lazy('Stwórz własny PDF')
    submit = gettext_lazy('Pobierz')
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

    template_name = 'catalogue/tag_catalogue.html'
    return render(request, template_name, {
        'tags': tags,
        'best': best,
        'title': constants.CATEGORIES_NAME_PLURAL[category],
        'whole_category': constants.WHOLE_CATEGORY[category],
    })


def collections(request):
    objects = Collection.objects.filter(listed=True)

    if len(objects) > 3:
        best = random.sample(list(objects), 4)
    else:
        best = objects

    template_name = 'catalogue/collections.html'
    return render(request, template_name, {
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
