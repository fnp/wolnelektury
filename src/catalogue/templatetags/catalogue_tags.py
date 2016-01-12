# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from random import randint, random
from urlparse import urlparse
from django.contrib.contenttypes.models import ContentType

from django.conf import settings
from django import template
from django.template import Node, Variable, Template, Context
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.cache import add_never_cache_headers
from django.utils.translation import ugettext as _

from ssify import ssi_variable
from catalogue.models import Book, BookMedia, Fragment, Tag, Source
from catalogue.constants import LICENSES
from picture.models import Picture

register = template.Library()


class RegistrationForm(UserCreationForm):
    def as_ul(self):
        """Returns this form rendered as HTML <li>s -- excluding the <ul></ul>."""
        return self._html_output(
            u'<li>%(errors)s%(label)s %(field)s<span class="help-text">%(help_text)s</span></li>', u'<li>%s</li>',
            '</li>', u' %s', False)


class LoginForm(AuthenticationForm):
    def as_ul(self):
        """Returns this form rendered as HTML <li>s -- excluding the <ul></ul>."""
        return self._html_output(
            u'<li>%(errors)s%(label)s %(field)s<span class="help-text">%(help_text)s</span></li>', u'<li>%s</li>',
            '</li>', u' %s', False)


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
    return capfirst(",<br/>".join(
        template.render(Context({'tag': tag, 'category': _(tag.category)})) for tag in tags))


def simple_title(tags):
    title = []
    for tag in tags:
        title.append("%s: %s" % (_(tag.category), tag.name))
    return capfirst(', '.join(title))


@register.simple_tag
def book_title(book, html_links=False):
    return book.pretty_title(html_links)


@register.simple_tag
def book_title_html(book):
    return book_title(book, html_links=True)


@register.simple_tag
def title_from_tags(tags):
    def split_tags(tags):
        result = {}
        for tag in tags:
            result[tag.category] = tag
        return result

    # TODO: Remove this after adding flection mechanism
    return simple_title(tags)

    class Flection(object):
        def get_case(self, name, flection):
            return name
    flection = Flection()

    self = split_tags(tags)

    title = u''

    # Specjalny przypadek oglądania wszystkich lektur na danej półce
    if len(self) == 1 and 'set' in self:
        return u'Półka %s' % self['set']

    # Specjalny przypadek "Twórczość w pozytywizmie", wtedy gdy tylko epoka
    # jest wybrana przez użytkownika
    if 'epoch' in self and len(self) == 1:
        text = u'Twórczość w %s' % flection.get_case(unicode(self['epoch']), u'miejscownik')
        return capfirst(text)

    # Specjalny przypadek "Dramat w twórczości Sofoklesa", wtedy gdy podane
    # są tylko rodzaj literacki i autor
    if 'kind' in self and 'author' in self and len(self) == 2:
        text = u'%s w twórczości %s' % (
            unicode(self['kind']), flection.get_case(unicode(self['author']), u'dopełniacz'))
        return capfirst(text)

    # Przypadki ogólniejsze
    if 'theme' in self:
        title += u'Motyw %s' % unicode(self['theme'])

    if 'genre' in self:
        if 'theme' in self:
            title += u' w %s' % flection.get_case(unicode(self['genre']), u'miejscownik')
        else:
            title += unicode(self['genre'])

    if 'kind' in self or 'author' in self or 'epoch' in self:
        if 'genre' in self or 'theme' in self:
            if 'kind' in self:
                title += u' w %s ' % flection.get_case(unicode(self['kind']), u'miejscownik')
            else:
                title += u' w twórczości '
        else:
            title += u'%s ' % unicode(self.get('kind', u'twórczość'))

    if 'author' in self:
        title += flection.get_case(unicode(self['author']), u'dopełniacz')
    elif 'epoch' in self:
        title += flection.get_case(unicode(self['epoch']), u'dopełniacz')

    return capfirst(title)


@register.simple_tag
def book_tree(book_list, books_by_parent):
    text = "".join("<li><a href='%s'>%s</a>%s</li>" % (
        book.get_absolute_url(), book.title, book_tree(books_by_parent.get(book, ()), books_by_parent)
        ) for book in book_list)

    if text:
        return "<ol>%s</ol>" % text
    else:
        return ''


@register.simple_tag
def audiobook_tree(book_list, books_by_parent):
    text = "".join("<li><a class='open-player' href='%s'>%s</a>%s</li>" % (
        reverse("book_player", args=[book.slug]), book.title,
        audiobook_tree(books_by_parent.get(book, ()), books_by_parent)
    ) for book in book_list)

    if text:
        return "<ol>%s</ol>" % text
    else:
        return ''


@register.simple_tag
def book_tree_texml(book_list, books_by_parent, depth=1):
    return "".join("""
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
            } for book in book_list)


@register.simple_tag
def book_tree_csv(author, book_list, books_by_parent, depth=1, max_depth=3, delimeter="\t"):
    def quote_if_necessary(s):
        try:
            s.index(delimeter)
            s.replace('"', '\\"')
            return '"%s"' % s
        except ValueError:
            return s

    return "".join("""%(author)s%(d)s%(preindent)s%(title)s%(d)s%(postindent)s%(audiences)s%(d)s%(audiobook)s
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
            } for book in book_list)


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


@register.simple_tag
def user_creation_form():
    return RegistrationForm(prefix='registration').as_ul()


@register.simple_tag
def authentication_form():
    return LoginForm(prefix='login').as_ul()


@register.tag
def catalogue_url(parser, token):
    bits = token.split_contents()

    tags_to_add = []
    tags_to_remove = []
    for bit in bits[1:]:
        if bit[0] == '-':
            tags_to_remove.append(bit[1:])
        else:
            tags_to_add.append(bit)

    return CatalogueURLNode(tags_to_add, tags_to_remove)


@register.tag
def catalogue_url_gallery(parser, token):
    bits = token.split_contents()

    tags_to_add = []
    tags_to_remove = []
    for bit in bits[1:]:
        if bit[0] == '-':
            tags_to_remove.append(bit[1:])
        else:
            tags_to_add.append(bit)

    return CatalogueURLNode(tags_to_add, tags_to_remove, gallery=True)


class CatalogueURLNode(Node):
    def __init__(self, tags_to_add, tags_to_remove, gallery=False):
        self.tags_to_add = [Variable(tag) for tag in tags_to_add]
        self.tags_to_remove = [Variable(tag) for tag in tags_to_remove]
        self.gallery = gallery

    def render(self, context):
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
            if self.gallery:
                return reverse('tagged_object_list_gallery', kwargs={'tags': '/'.join(tag_slugs)})
            else:
                return reverse('tagged_object_list', kwargs={'tags': '/'.join(tag_slugs)})
        else:
            return reverse('book_list')


@register.inclusion_tag('catalogue/tag_list.html')
def tag_list(tags, choices=None, category=None, gallery=False):
    print(tags, choices, category)
    if choices is None:
        choices = []

    if category is None and tags:
        category = tags[0].category

    category_choices = [tag for tag in choices if tag.category == category]

    if len(tags) == 1 and category not in [t.category for t in choices]:
        one_tag = tags[0]

    if category is not None:
        other = Tag.objects.filter(category=category).exclude(pk__in=[t.pk for t in tags])\
            .exclude(pk__in=[t.pk for t in category_choices])
        # Filter out empty tags.
        ct = ContentType.objects.get_for_model(Picture if gallery else Book)
        other = other.filter(items__content_type=ct).distinct()

    return locals()


@register.inclusion_tag('catalogue/inline_tag_list.html')
def inline_tag_list(tags, choices=None, category=None, gallery=False):
    return tag_list(tags, choices, category, gallery)


@register.inclusion_tag('catalogue/collection_list.html')
def collection_list(collections):
    return locals()


@register.inclusion_tag('catalogue/book_info.html')
def book_info(book):
    return {
        'is_picture': isinstance(book, Picture),
        'book': book,
    }


@register.inclusion_tag('catalogue/work-list.html', takes_context=True)
def work_list(context, object_list):
    request = context.get('request')
    return locals()


@register.inclusion_tag('catalogue/plain_list.html', takes_context=True)
def plain_list(context, object_list, with_initials=True, by_author=False, choice=None, book=None, gallery=False,
               paged=True):
    names = [('', [])]
    last_initial = None
    for obj in object_list:
        if with_initials:
            if by_author:
                initial = obj.sort_key_author
            else:
                initial = obj.get_initial().upper()
            if initial != last_initial:
                last_initial = initial
                names.append((obj.author_str() if by_author else initial, []))
        names[-1][1].append(obj)
    return locals()


# TODO: These are no longer just books.
@register.inclusion_tag('catalogue/related_books.html', takes_context=True)
def related_books(context, instance, limit=6, random=1, taken=0):
    limit -= taken
    max_books = limit - random
    is_picture = isinstance(instance, Picture)

    pics_qs = Picture.objects.all()
    if is_picture:
        pics_qs = pics_qs.exclude(pk=instance.pk)
    pics = Picture.tagged.related_to(instance, pics_qs)
    if pics.exists():
        # Reserve one spot for an image.
        max_books -= 1

    books_qs = Book.objects.all()
    if not is_picture:
        books_qs = books_qs.exclude(common_slug=instance.common_slug).exclude(ancestor=instance)
    books = Book.tagged.related_to(instance, books_qs)[:max_books]

    pics = pics[:1 + max_books - books.count()]

    random_excluded_books = [b.pk for b in books]
    random_excluded_pics = [p.pk for p in pics]
    (random_excluded_pics if is_picture else random_excluded_books).append(instance.pk)

    return {
        'request': context['request'],
        'books': books,
        'pics': pics,
        'random': random,
        'random_excluded_books': random_excluded_books,
        'random_excluded_pics': random_excluded_pics,
    }


@register.simple_tag
def download_audio(book, daisy=True):
    links = []
    if book.has_media('mp3'):
        links.append("<a href='%s'>%s</a>" % (
            reverse('download_zip_mp3', args=[book.slug]), BookMedia.formats['mp3'].name))
    if book.has_media('ogg'):
        links.append("<a href='%s'>%s</a>" % (
            reverse('download_zip_ogg', args=[book.slug]), BookMedia.formats['ogg'].name))
    if daisy and book.has_media('daisy'):
        for dsy in book.get_media('daisy'):
            links.append("<a href='%s'>%s</a>" % (dsy.file.url, BookMedia.formats['daisy'].name))
    return "".join(links)


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


@register.filter
def class_name(obj):
    return obj.__class__.__name__


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


@ssi_variable(register, patch_response=[add_never_cache_headers])
def catalogue_random_book(request, exclude_ids):
    from .. import app_settings
    if random() < app_settings.RELATED_RANDOM_PICTURE_CHANCE:
        return None
    queryset = Book.objects.exclude(pk__in=exclude_ids)
    count = queryset.count()
    if count:
        return queryset[randint(0, count - 1)].pk
    else:
        return None


@ssi_variable(register, patch_response=[add_never_cache_headers])
def choose_fragment(request, book_id=None, tag_ids=None, unless=False):
    if unless:
        return None

    if book_id is not None:
        fragment = Book.objects.get(pk=book_id).choose_fragment()
    else:
        if tag_ids is not None:
            tags = Tag.objects.filter(pk__in=tag_ids)
            fragments = Fragment.tagged.with_all(tags).order_by().only('id')
        else:
            fragments = Fragment.objects.all().order_by().only('id')
        fragment_count = fragments.count()
        fragment = fragments[randint(0, fragment_count - 1)] if fragment_count else None
    return fragment.pk if fragment is not None else None
