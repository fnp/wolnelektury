# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from random import randint, random
from urllib.parse import urlparse
from django.contrib.contenttypes.models import ContentType

from django.conf import settings
from django import template
from django.template import Node, Variable, Template, Context
from django.urls import reverse
from django.utils.cache import add_never_cache_headers
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from catalogue.helpers import get_audiobook_tags
from catalogue.models import Book, BookMedia, Fragment, Tag, Source
from catalogue.constants import LICENSES
from club.models import Membership

register = template.Library()


def iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def capfirst(text):
    try:
        return '%s%s' % (text[0].upper(), text[1:])
    except IndexError:
        return ''


@register.simple_tag
def html_title_from_tags(tags):
    if len(tags) < 2:
        return title_from_tags(tags)
    template = Template("{{ category }}: <a href='{{ tag.get_absolute_url }}'>{{ tag.name }}</a>")
    return mark_safe(capfirst(",<br/>".join(
        template.render(Context({'tag': tag, 'category': tag.get_category_display()})) for tag in tags)))


def simple_title(tags):
    title = []
    for tag in tags:
        title.append("%s: %s" % (tag.get_category_display(), tag.name))
    return capfirst(', '.join(title))


@register.simple_tag
def book_title(book, html_links=False):
    return mark_safe(book.pretty_title(html_links))


@register.simple_tag
def book_title_html(book):
    return book_title(book, html_links=True)


@register.simple_tag
def title_from_tags(tags):
    # TODO: Remove this after adding flection mechanism
    return simple_title(tags)


@register.simple_tag
def nice_title_from_tags(tags, related_tags):
    def split_tags(tags):
        result = {}
        for tag in tags:
            result.setdefault(tag.category, []).append(tag)
        return result

    self = split_tags(tags)

    pieces = []
    plural = True
    epoch_reduntant = False

    if 'genre' in self:
        pieces.append([
            t.plural or t.name for t in self['genre']
        ])
        epoch_reduntant = self['genre'][-1].genre_epoch_specific
    else:
        # If we don't have genre,
        # look if maybe we only have one genre in this context?
        if 'genre' in related_tags and len(related_tags['genre']) == 1:
            pieces.append([
                t.plural or t.name for t in related_tags['genre']
            ])
            epoch_reduntant = related_tags['genre'][-1].genre_epoch_specific
        elif 'kind' in self:
            # Only use kind if not talking about genre.
            pieces.append([
                t.collective_noun or t.name for t in self['kind']
            ])
            plural = False
        elif 'kind' in related_tags and len(related_tags['kind']) == 1:
            # No info on genre, but there's only one kind related.
            subpieces = []
            pieces.append([
                t.collective_noun or t.name for t in related_tags['kind']
            ])
            plural = False
        else:
            # We can't say anything about genre or kind.
            pieces.append(['Twórczość'])
            plural = False

    if not epoch_reduntant and 'epoch' in self:
        if plural:
            form = lambda t: t.adjective_nonmasculine_plural or t.name
        else:
            form = lambda t: t.adjective_feminine_singular or t.name
        pieces.append([
            form(t) for t in self['epoch']
        ])

    if 'author' in self:
        pieces.append([
            t.genitive or t.name for t in self['author']
        ])
    
    p = []
    for sublist in pieces:
        for item in sublist[:-2]:
            p.append(item + ',')
        for item in sublist[-2:-1]:
            p.append(item + ' i')
        p.append(sublist[-1])

    return ' '.join(p)


@register.simple_tag
def book_tree(book_list, books_by_parent):
    text = "".join("<li><a href='%s'>%s</a>%s</li>" % (
        book.get_absolute_url(), book.title, book_tree(books_by_parent.get(book, ()), books_by_parent)
        ) for book in book_list)

    if text:
        return mark_safe("<ol>%s</ol>" % text)
    else:
        return ''


@register.simple_tag
def book_tree_texml(book_list, books_by_parent, depth=1):
    return mark_safe("".join("""
            <cmd name='hspace'><parm>%(depth)dem</parm></cmd>%(title)s
            <spec cat='align' /><cmd name="note"><parm>%(audiences)s</parm></cmd>
            <spec cat='align' /><cmd name="note"><parm>%(audiobook)s</parm></cmd>
            <ctrl ch='\\' />
            %(children)s
            """ % {
                "depth": depth,
                "title": book.title,
                "audiences": ", ".join(book.audiences_pl()),
                "audiobook": "audiobook" if book.has_media('mp3') else "",
                "children": book_tree_texml(books_by_parent.get(book.id, ()), books_by_parent, depth + 1)
            } for book in book_list))


@register.simple_tag
def book_tree_csv(author, book_list, books_by_parent, depth=1, max_depth=3, delimeter="\t"):
    def quote_if_necessary(s):
        try:
            s.index(delimeter)
            s.replace('"', '\\"')
            return '"%s"' % s
        except ValueError:
            return s

    return mark_safe("".join("""%(author)s%(d)s%(preindent)s%(title)s%(d)s%(postindent)s%(audiences)s%(d)s%(audiobook)s
%(children)s""" % {
                "d": delimeter,
                "preindent": delimeter * (depth - 1),
                "postindent": delimeter * (max_depth - depth),
                "depth": depth,
                "author": quote_if_necessary(author.name),
                "title": quote_if_necessary(book.title),
                "audiences": ", ".join(book.audiences_pl()),
                "audiobook": "audiobook" if book.has_media('mp3') else "",
                "children": book_tree_csv(author, books_by_parent.get(book.id, ()), books_by_parent, depth + 1)
            } for book in book_list))


@register.simple_tag
def all_editors(extra_info):
    editors = []
    if 'editors' in extra_info:
        editors += extra_info['editors']
    if 'technical_editors' in extra_info:
        editors += extra_info['technical_editors']
    # support for extra_info-s from librarian<1.2
    if 'editor' in extra_info:
        editors.append(extra_info['editor'])
    if 'technical_editor' in extra_info:
        editors.append(extra_info['technical_editor'])
    return ', '.join(
                     ' '.join(p.strip() for p in person.rsplit(',', 1)[::-1])
                     for person in sorted(set(editors)))


@register.tag
def catalogue_url(parser, token):
    bits = token.split_contents()

    tags_to_add = []
    tags_to_remove = []
    for bit in bits[2:]:
        if bit[0] == '-':
            tags_to_remove.append(bit[1:])
        else:
            tags_to_add.append(bit)

    return CatalogueURLNode(bits[1], tags_to_add, tags_to_remove)


class CatalogueURLNode(Node):
    def __init__(self, list_type, tags_to_add, tags_to_remove):
        self.tags_to_add = [Variable(tag) for tag in tags_to_add]
        self.tags_to_remove = [Variable(tag) for tag in tags_to_remove]
        self.list_type_var = Variable(list_type)

    def render(self, context):
        list_type = self.list_type_var.resolve(context)
        tags_to_add = []
        tags_to_remove = []

        for tag_variable in self.tags_to_add:
            tag = tag_variable.resolve(context)
            if isinstance(tag, (list, dict)):
                tags_to_add += [t for t in tag]
            else:
                tags_to_add.append(tag)

        for tag_variable in self.tags_to_remove:
            tag = tag_variable.resolve(context)
            if iterable(tag):
                tags_to_remove += [t for t in tag]
            else:
                tags_to_remove.append(tag)

        tag_slugs = [tag.url_chunk for tag in tags_to_add]
        for tag in tags_to_remove:
            try:
                tag_slugs.remove(tag.url_chunk)
            except KeyError:
                pass

        if len(tag_slugs) > 0:
            if list_type == 'audiobooks':
                return reverse('tagged_object_list_audiobooks', kwargs={'tags': '/'.join(tag_slugs)})
            else:
                return reverse('tagged_object_list', kwargs={'tags': '/'.join(tag_slugs)})
        else:
            if list_type == 'audiobooks':
                return reverse('audiobook_list')
            else:
                return reverse('book_list')


@register.inclusion_tag('catalogue/book_info.html')
def book_info(book):
    return {
        'book': book,
    }


@register.inclusion_tag('catalogue/plain_list.html', takes_context=True)
def plain_list(context, object_list, with_initials=True, by_author=False, choice=None, book=None, list_type='books',
               paged=True, initial_blocks=False):
    names = [('', [])]
    last_initial = None
    if len(object_list) < settings.CATALOGUE_MIN_INITIALS and not by_author:
        with_initials = False
        initial_blocks = False
    for obj in object_list:
        if with_initials:
            if by_author:
                initial = obj.sort_key_author
            else:
                initial = obj.get_initial().upper()
            if initial != last_initial:
                last_initial = initial
                names.append((obj.author_unicode() if by_author else initial, []))
        names[-1][1].append(obj)
    if names[0] == ('', []):
        del names[0]
    return {
        'paged': paged,
        'names': names,
        'initial_blocks': initial_blocks,
        'book': book,
        'list_type': list_type,
        'choice': choice,
    }


@register.simple_tag
def related_books_2022(book=None, limit=4, taken=0):
    limit -= taken
    max_books = limit

    books_qs = Book.objects.filter(findable=True)
    if book is not None:
        books_qs = books_qs.exclude(common_slug=book.common_slug).exclude(ancestor=book)
    books = Book.tagged.related_to(book, books_qs)[:max_books]

    return books


@register.simple_tag
def download_audio(book, daisy=True, mp3=True):
    links = []
    if mp3 and book.has_media('mp3'):
        links.append("<a href='%s'>%s</a>" % (
            reverse('download_zip_mp3', args=[book.slug]), BookMedia.formats['mp3'].name))
    if book.has_media('ogg'):
        links.append("<a href='%s'>%s</a>" % (
            reverse('download_zip_ogg', args=[book.slug]), BookMedia.formats['ogg'].name))
    if daisy and book.has_media('daisy'):
        for dsy in book.get_media('daisy'):
            links.append("<a href='%s'>%s</a>" % (dsy.file.url, BookMedia.formats['daisy'].name))
    if daisy and book.has_media('audio.epub'):
        for dsy in book.get_media('audio.epub'):
            links.append("<a href='%s'>%s</a>" % (dsy.file.url, BookMedia.formats['audio.epub'].name))
    return mark_safe("".join(links))


@register.inclusion_tag("catalogue/snippets/custom_pdf_link_li.html")
def custom_pdf_link_li(book):
    return {
        'book': book,
        'NO_CUSTOM_PDF': settings.NO_CUSTOM_PDF,
    }


@register.inclusion_tag("catalogue/snippets/license_icon.html")
def license_icon(license_url):
    """Creates a license icon, if the license_url is known."""
    known = LICENSES.get(license_url)
    if known is None:
        return {}
    return {
        "license_url": license_url,
        "icon": "img/licenses/%s.png" % known['icon'],
        "license_description": known['description'],
    }


@register.simple_tag
def license_locative(license_url, default):
    return LICENSES.get(license_url, {}).get('locative', default)


@register.simple_tag
def source_name(url):
    url = url.lstrip()
    netloc = urlparse(url).netloc
    if not netloc:
        netloc = urlparse('http://' + url).netloc
    if not netloc:
        return ''
    source, created = Source.objects.get_or_create(netloc=netloc)
    return source.name or netloc


@register.simple_tag
def catalogue_random_book(exclude_ids):
    from .. import app_settings
    if random() < app_settings.RELATED_RANDOM_PICTURE_CHANCE:
        return None
    queryset = Book.objects.filter(findable=True).exclude(pk__in=exclude_ids)
    count = queryset.count()
    if count:
        return queryset[randint(0, count - 1)]
    else:
        return None


@register.simple_tag
def choose_fragment(book=None, tag_ids=None):
    if book is not None:
        fragment = book.choose_fragment()
    else:
        if tag_ids is not None:
            tags = Tag.objects.filter(pk__in=tag_ids)
            fragments = Fragment.tagged.with_all(tags).filter(book__findable=True).order_by().only('id')
        else:
            fragments = Fragment.objects.filter(book__findable=True).order_by().only('id')
        fragment_count = fragments.count()
        fragment = fragments[randint(0, fragment_count - 1)] if fragment_count else None
    return fragment


@register.filter
def strip_tag(html, tag_name):
    # docelowo może być warto zainstalować BeautifulSoup do takich rzeczy
    import re
    return re.sub(r"<.?%s\b[^>]*>" % tag_name, "", html)


@register.filter
def status(book, user):
    if not book.preview:
        return 'open'
    elif book.is_accessible_to(user):
        return 'preview'
    else:
        return 'closed'


@register.inclusion_tag('catalogue/snippets/content_warning.html')
def content_warning(book):
    warnings_def = {
        'wulgaryzmy': _('wulgaryzmy'),
    }
    warnings = book.get_extra_info_json().get('content_warnings', [])
    warnings = sorted(
        warnings_def.get(w, w)
        for w in warnings
    )
    return {
        "warnings": warnings
    }


@register.inclusion_tag('catalogue/preview_ad.html', takes_context=True)
def preview_ad(context):
    book = Book.objects.filter(parent=None, preview=True).first()
    if book is None:
        return {}
    return {
        'accessible': book.is_accessible_to(context['request'].user),
        'book': book,
    }

@register.inclusion_tag('catalogue/preview_ad_homepage.html', takes_context=True)
def preview_ad_homepage(context):
    book = Book.objects.filter(parent=None, preview=True).first()
    if book is None:
        return {}
    return {
        'accessible': book.is_accessible_to(context['request'].user),
        'book': book,
    }
